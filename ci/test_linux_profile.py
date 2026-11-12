"""Linux lifecycle fixtures use a fake manager; never control host services."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANAGER = r'''#!/usr/bin/python3
import hashlib, json, os, pathlib, re, sys
home = pathlib.Path(os.environ['HOME'])
record = home / 'manager.json'
state = json.loads(record.read_text()) if record.exists() else {}
unit = home / '.config/systemd/user/graph-community.service'
body = unit.read_bytes() if unit.exists() else b''
digest = hashlib.sha256(body).hexdigest()
args = sys.argv[1:]
assert args[0] == '--user'
action = args[1]
state.setdefault('calls', []).append(action)
def save(): record.write_text(json.dumps(state))
if action == 'show':
    values = dict(LoadState='loaded' if unit.exists() else 'not-found',
                  FragmentPath=str(unit) if unit.exists() else '', DropInPaths='',
                  ActiveState='active' if state.get('active') else 'inactive',
                  MainPID='123' if state.get('active') else '0',
                  TasksCurrent='1' if state.get('active') else '0', UnitFileState='disabled',
                  NeedDaemonReload='no' if not body or state.get('digest') == digest else 'yes')
    values.update(state.get('properties', {}))
    print('\n'.join(key + '=' + value for key, value in values.items()))
elif action == 'daemon-reload':
    if state.pop('fail_reload', False):
        save()
        print('synthetic reload failure', file=sys.stderr)
        raise SystemExit(1)
    state['digest'] = digest
elif action == 'start':
    state['active'] = True
    environment = {}
    for line in body.decode().splitlines():
        if line.startswith('Environment='):
            raw = line[len('Environment="'):-1]
            value = re.sub(r'\\(["\\])', r'\1', raw).replace('%%', '%')
            key, value = value.split('=', 1)
            environment[key] = value
    state['started_environment'] = environment
else:
    raise AssertionError('Unexpected manager call: ' + action)
save()
'''


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux Bash lifecycle only')
class LinuxProfiles(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='Community Linux profile ')
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.source = self.home / 'source % spaces'
        (self.source / 'bin').mkdir(parents=True)
        shutil.copy2(ROOT / 'bin/graph', self.source / 'bin/graph')
        self.bin = self.home / 'fake bin'
        self.bin.mkdir()
        for tool, content in (('systemctl', MANAGER), ('gh', '#!/bin/sh\nexit 0\n'),
                              ('codex', '#!/bin/sh\nexit 0\n')):
            path = self.bin / tool
            path.write_text(content)
            path.chmod(0o755)
        self.env = dict(HOME=str(self.home), PATH=str(self.bin) + os.pathsep + os.defpath,
                        PYTHONDONTWRITEBYTECODE='1')
        self.unit = self.home / '.config/systemd/user/graph-community.service'
        self.record = self.home / 'manager.json'

    def profile(self, name='selected "profile" % $ \\'):
        base = self.home / name
        return dict(VEZRYN_GRAPH_CONFIG=str(base / 'config/repos.toml'),
                    VEZRYN_GRAPH_STATE=str(base / 'state'),
                    VEZRYN_GRAPH_LIBRARY=str(base / 'guidance'))

    def run_graph(self, action, profile=None, ok=True):
        env = {**self.env, **(profile or {})}
        result = subprocess.run(['/bin/bash', str(self.source / 'bin/graph'), action],
                                env=env, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def manager(self, **changes):
        current = json.loads(self.record.read_text()) if self.record.exists() else {}
        current.update(changes)
        self.record.write_text(json.dumps(current))
        return current

    def test_selected_profile_is_bound_and_mismatched_controls_do_not_write_state(self):
        profile = self.profile()
        self.run_graph('install', profile)
        self.run_graph('start', profile)
        started = self.manager()['started_environment']
        self.assertEqual({key: started[key] for key in profile}, profile)
        self.assertIn('%%', self.unit.read_text())
        self.run_graph('stop', profile)
        marker = Path(profile['VEZRYN_GRAPH_STATE']) / 'stop-request'
        self.assertTrue(marker.is_file())
        self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.home / '.local/state/graph-community').exists())
        before = self.unit.read_bytes()
        other = self.profile('different profile')
        self.assertIn('active or unverified', self.run_graph('install', self.profile('rebind while active'), ok=False).stderr)
        self.assertEqual(self.unit.read_bytes(), before)
        for action in ('start', 'stop', 'uninstall'):
            with self.subTest(action=action):
                self.assertIn('Selected profile differs', self.run_graph(action, other, ok=False).stderr)
                self.assertFalse(Path(other['VEZRYN_GRAPH_STATE']).exists())
                self.assertEqual(self.unit.read_bytes(), before)
        self.manager(active=False)
        self.run_graph('uninstall', profile)
        self.assertFalse(self.unit.exists())
        self.assertTrue(marker.exists())  # No operational evidence is removed.
        self.assertNotIn('stop', self.manager()['calls'])

    def test_defaults_and_expansion_match_the_bound_absolute_profile(self):
        self.run_graph('install')
        self.run_graph('start')
        expected = dict(VEZRYN_GRAPH_CONFIG=str(self.home / '.config/graph-community/repos.toml'),
                        VEZRYN_GRAPH_STATE=str(self.home / '.local/state/graph-community'),
                        VEZRYN_GRAPH_LIBRARY=str(self.home / '.config/graph-community/library'))
        env = self.manager()['started_environment']
        self.assertEqual({key: env[key] for key in expected}, expected)
        self.run_graph('stop', {key: value.replace(str(self.home), '~', 1) for key, value in expected.items()})

    def test_legacy_units_require_idle_explicit_rebind(self):
        self.run_graph('install')
        bound = self.unit.read_text()
        legacy = '\n'.join(line for line in bound.splitlines()
                           if not line.startswith('Environment="VEZRYN_GRAPH_')) + '\n'
        unquoted = ('[Unit]\nDescription=Graph Community GitHub issue watcher\n\n[Service]\n'
                    'Type=simple\nWorkingDirectory=' + str(self.source) + '\n'
                    'Environment="PATH=' + self.env['PATH'] + '"\n'
                    'ExecStart=/usr/bin/python3 -u ' + str(self.source / 'watcher.py') + ' watch\nRestart=no\n')
        import hashlib
        for index, predecessor in enumerate((legacy, unquoted)):
            with self.subTest(predecessor=index):
                self.unit.write_text(predecessor)
                # Simulate a loaded old source-owned unit; no real manager.
                self.manager(active=True, digest=hashlib.sha256(predecessor.encode()).hexdigest())
                custom = self.profile('legacy selection ' + str(index))
                for action in ('start', 'stop', 'uninstall'):
                    self.assertIn('Legacy service has no bound profile', self.run_graph(action, custom, ok=False).stderr)
                self.assertFalse(Path(custom['VEZRYN_GRAPH_STATE']).exists())
                self.assertIn('active or unverified', self.run_graph('install', custom, ok=False).stderr)
                self.assertEqual(self.unit.read_text(), predecessor)
                self.manager(active=False)
                self.run_graph('install', custom)
                self.run_graph('start', custom)
                self.assertEqual(self.manager()['started_environment']['VEZRYN_GRAPH_STATE'], custom['VEZRYN_GRAPH_STATE'])

    def test_reload_rollback_and_foreign_or_stale_identity_are_preserved(self):
        first, second = self.profile('first'), self.profile('second')
        self.run_graph('install', first)
        before = self.unit.read_bytes()
        self.manager(fail_reload=True)
        result = self.run_graph('install', second, ok=False)
        self.assertIn('owned file changes rolled back', result.stderr)
        self.assertEqual(self.unit.read_bytes(), before)
        self.run_graph('start', first)
        self.manager(active=False, fail_reload=True)
        self.assertIn('owned file changes rolled back', self.run_graph('uninstall', first, ok=False).stderr)
        self.assertEqual(self.unit.read_bytes(), before)
        self.assertEqual(os.readlink(self.home / '.local/bin/graph'), str(self.source / 'bin/graph'))
        self.manager(active=False, properties={'NeedDaemonReload': 'yes'})
        self.assertIn('identity is unverified', self.run_graph('stop', first, ok=False).stderr)
        self.manager(properties={})
        self.unit.write_bytes(before + b'Environment="EXTRA=value"\n')
        self.assertIn('nonowned', self.run_graph('install', first, ok=False).stderr)
        self.assertEqual(self.unit.read_bytes(), before + b'Environment="EXTRA=value"\n')

    def test_invalid_environment_and_foreign_links_fail_before_writes(self):
        invalid = self.profile()
        invalid['VEZRYN_GRAPH_LIBRARY'] += '\ninvalid'
        self.assertIn('Unsupported control', self.run_graph('install', invalid, ok=False).stderr)
        self.assertFalse(self.unit.parent.exists())
        self.unit.parent.mkdir(parents=True)
        foreign = self.home / 'unrelated unit'
        foreign.write_text('preserve')
        self.unit.symlink_to(foreign)
        self.run_graph('install', self.profile(), ok=False)
        self.assertTrue(self.unit.is_symlink())
        self.assertEqual(foreign.read_text(), 'preserve')

    def test_service_control_lock_also_excludes_a_different_profile(self):
        import fcntl
        first, second = self.profile('first'), self.profile('second')
        self.run_graph('install', first)
        before = self.unit.read_bytes()
        with (self.unit.parent / '.graph-community-control.lock').open('r+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn('control is in progress', self.run_graph('install', second, ok=False).stderr)
        self.assertEqual(self.unit.read_bytes(), before)
        self.assertFalse(Path(second['VEZRYN_GRAPH_STATE']).exists())


if __name__ == '__main__':
    unittest.main()
