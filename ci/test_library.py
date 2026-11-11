"""Offline library/packaging regressions; fake client, no model or GitHub calls."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import library
import watcher

spec = importlib.util.spec_from_file_location('package_check', ROOT / 'ci/check.py')
package_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_check)


class LibraryTests(unittest.TestCase):
    def test_fresh_defaults_overrides_disable_and_replacement(self):
        with tempfile.TemporaryDirectory(prefix='Community library ') as folder:
            base = Path(folder)
            install, overrides = base / 'app', base / 'local library'
            for name in ('policies', 'playbooks', 'skills'):
                shutil.copytree(ROOT / name, install / name)
            initial = library.resolve(install, overrides)
            self.assertEqual(len(initial), 38)
            self.assertEqual(sum(name.startswith('playbooks/') for name in initial), 22)
            self.assertEqual(sum(name.startswith('skills/') for name in initial), 10)
            self.assertTrue(all(path.is_relative_to(install) for path in initial.values()))
            self.assertFalse(any('creative-' in name for name in initial))
            with patch.object(watcher, 'CONFIG', base / 'config/repos.toml'):
                self.assertEqual(watcher.enrolled(), [])
            replacement = overrides / 'playbooks/implement-and-deliver.md'
            replacement.parent.mkdir(parents=True)
            replacement.write_text('# Local delivery\nUse the authorized local workflow.\n')
            self.assertEqual(library.resolve(install, overrides)[replacement.relative_to(overrides).as_posix()], replacement)
            # Replacing installed defaults must not replace operator files.
            (install / 'playbooks/implement-and-deliver.md').write_text('# Changed installed default\n')
            self.assertEqual(library.resolve(install, overrides)['playbooks/implement-and-deliver.md'].read_text(), replacement.read_text())
            marker = replacement.with_name(replacement.name + '.disabled')
            marker.touch()
            self.assertNotIn('playbooks/implement-and-deliver.md', library.resolve(install, overrides))
            marker.unlink()
            replacement.unlink()
            self.assertEqual(library.resolve(install, overrides)['playbooks/implement-and-deliver.md'], install / 'playbooks/implement-and-deliver.md')
            skill = overrides / 'skills/change-aware-verification/SKILL.md.disabled'
            skill.parent.mkdir(parents=True)
            skill.touch()
            self.assertNotIn('skills/change-aware-verification/SKILL.md', library.resolve(install, overrides))
            custom = base / 'custom/playbooks/local-check.md'
            custom.parent.mkdir(parents=True)
            custom.write_text('# Local check\n')
            with patch.dict(os.environ, {'VEZRYN_GRAPH_LIBRARY': str(custom.parents[1])}):
                prompt = watcher.coordinator_prompt(['example/project'])
                self.assertIn(str(custom), prompt)
                self.assertNotIn(str(overrides), prompt)

    @unittest.skipIf(os.name == 'nt', 'POSIX fake-client executable; not a native Windows trial')
    def test_routed_literal_handoff_through_existing_launch(self):
        with tempfile.TemporaryDirectory(prefix='Community handoff ') as folder:
            base = Path(folder)
            client, packet = base / 'fake-client', base / 'packet.json'
            client.write_text(f'''#!{sys.executable}
import json, os, pathlib, sys
prompt = sys.stdin.read()
paths = dict((line[2:].split(" => ", 1)[0], json.loads(line[2:].split(" => ", 1)[1]))
             for line in prompt.splitlines() if line.startswith("- ") and " => " in line)
selected = json.loads(os.environ["TEST_SELECTED"])
missing = [name for name in selected if name not in paths]
pathlib.Path(os.environ["TEST_PACKET"]).write_text(json.dumps({{"argv": sys.argv[1:], "missing": missing,
 "original_issue": os.environ["TEST_ISSUE"],
 "instructions": [pathlib.Path(paths[name]).read_text() for name in selected if name in paths]}}))
''')
            client.chmod(0o755)
            overrides = base / 'overrides'
            replacement = overrides / 'playbooks/implement-and-deliver.md'
            replacement.parent.mkdir(parents=True)
            replacement.write_text('# Whole local replacement\nDeliver this exact text.\n')
            routes = (
                ('implement-and-deliver', 'change-aware-verification'),
                ('diagnose-and-repair', 'repair-and-resume'),
                ('document-and-verify', 'outcome-driven-engineering'),
                ('rapid-prototype', 'prototype-first'),
                ('investigate-and-recommend', 'execution-intent-preservation'),
                ('integrate-and-verify', 'source-custody'),
                ('pr-maintenance', 'change-aware-verification'),
                ('launch-and-observe', 'observable-progress'),
                ('pause-and-recover', 'context-continuity'),
            )
            state = base / 'state'
            env = {'VEZRYN_GRAPH_LIBRARY': str(overrides), 'TEST_PACKET': str(packet),
                   'TEST_ISSUE': 'https://github.com/example/project/issues/1'}
            # Only discovery/prerequisite checks are substituted. The real launch
            # function creates the process, streams its inventory and waits for it.
            with patch.dict(os.environ, env), patch.object(watcher, 'STATE', state), \
                 patch.object(watcher, 'STOP_REQUEST', state / 'stop-request'), \
                 patch.object(watcher.platform, 'launch_prerequisites'), \
                 patch.object(watcher.platform, 'executable', return_value=str(client)):
                for playbook, skill in routes:
                    selected = [f'playbooks/{playbook}.md', f'skills/{skill}/SKILL.md']
                    with self.subTest(playbook=playbook), patch.dict(os.environ, {'TEST_SELECTED': json.dumps(selected)}):
                        self.assertEqual(watcher.launch(['example/project']), 0)
                        result = json.loads(packet.read_text())
                        self.assertEqual(result['argv'], ['exec', '--json', '-C', str(ROOT), '-'])
                        self.assertEqual(result['original_issue'], env['TEST_ISSUE'])
                        self.assertEqual(result['missing'], [])
                        effective = library.resolve(ROOT, overrides)
                        self.assertEqual(result['instructions'], [effective[name].read_text() for name in selected])
                replacement.with_name(replacement.name + '.disabled').touch()
                with patch.dict(os.environ, {'TEST_SELECTED': json.dumps(['playbooks/implement-and-deliver.md'])}):
                    self.assertEqual(watcher.launch(['example/project']), 0)
                    result = json.loads(packet.read_text())
                    self.assertEqual(result['missing'], ['playbooks/implement-and-deliver.md'])
                    self.assertEqual(result['instructions'], [])

    def test_package_content_links_and_foreign_history_rejection(self):
        package_check.check_content('allowed', b'VEZRYN_GRAPH_CONFIG https://github.com/Vezryn-LLC/graph-community')
        for content in (b'/' + b'home/example/private', b'Vezryn' + b'-LLC/private-source',
                        b'gh' + b'p_' + b'x' * 24, b'-----BEGIN ' + b'PRIVATE KEY-----'):
            with self.subTest(content=content), self.assertRaises(AssertionError):
                package_check.check_content('contaminated', content)
        with tempfile.TemporaryDirectory(prefix='Community payload contamination ') as folder:
            root = Path(folder)
            for name in package_check.PAYLOAD_FILES | {'MANIFEST.json'}:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            # Editing the hash manifest cannot authorize an unreviewed source path.
            manifest = json.loads((root / 'MANIFEST.json').read_text())
            (root / 'operational.log').write_text('synthetic local state')
            manifest['files']['operational.log'] = {'sha256': 'unused', 'mode': '0o644'}
            (root / 'MANIFEST.json').write_text(json.dumps(manifest))
            rejected = subprocess.run([sys.executable, '-B', str(root / 'ci/check.py')],
                                      capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('operational.log', rejected.stderr)
        with tempfile.TemporaryDirectory(prefix='Community foreign history ') as folder:
            root = Path(folder)
            self.assertIn('archive', package_check.check_history(root))
            (root / 'a.md').write_text('[missing](missing.md)\n')
            with self.assertRaises(AssertionError):
                package_check.check_links(root, ['a.md'])
            (root / 'missing.md').write_text('# Present\n')
            self.assertEqual(package_check.check_links(root, ['a.md']), 1)
            subprocess.run(['git', '-c', 'init.templateDir=', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Example', '-c',
                            'user.email=example@example.invalid', '-c', 'core.hooksPath=' + os.devnull,
                            'commit', '-q', '--allow-empty', '-m', 'Unrelated root'], check=True)
            with self.assertRaisesRegex(AssertionError, 'Unexpected Git roots'):
                package_check.check_history(root)


if __name__ == '__main__':
    unittest.main()
