"""Offline status JSON fixtures; no account, runtime, service or source probes."""
import calendar
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import watcher


def receipt(stamp):
    return {'version': 1, 'pending': None, 'hold': None,
            'issues': {'example/project#1': {'last_checked': stamp,
                'observation': {'disposition': 'blocked'}, 'next_action': 'private-token'}},
            'last_run': {'exit_status': 0, 'session': 'private-token', 'launch_error': '/private/path'}}


class StatusTests(unittest.TestCase):
    def test_positive_stale_and_invalid_receipts_without_probes(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(watcher, 'STATE', Path(folder)), \
             patch.object(watcher.subprocess, 'run', side_effect=AssertionError('External probe')), \
             patch.object(watcher, 'activation_source', side_effect=AssertionError('Source probe')), \
             patch.object(watcher, 'enrolled', side_effect=AssertionError('Account/config probe')):
            path = Path(folder) / watcher.RUN_STATE
            self.assertEqual(watcher.status_report()['diagnostics']['status'], 'missing')
            now = calendar.timegm(time.strptime('2026-11-12T12:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
            for stamp, freshness, count in (('2026-11-12T11:59:00Z', 'fresh', 1),
                                            ('2026-11-12T11:55:00Z', 'fresh', 1),
                                            ('2026-11-12T11:54:59Z', 'stale', None)):
                path.write_text(json.dumps(receipt(stamp)))
                path.chmod(0o600)
                with patch.object(watcher.time, 'time', return_value=now):
                    report = watcher.status_report()
                self.assertEqual(report['diagnostics']['freshness'], freshness)
                self.assertEqual(report['diagnostics']['scoped_blocked_count'], count)
                self.assertEqual(report['last_coordinator']['exit_status'], 0)
                self.assertEqual(report['last_coordinator']['freshness'], 'unknown')
                self.assertIsNone(report['queue']['candidate_count'])
                self.assertIsNone(report['queue']['blocked_count'])
                self.assertNotIn('private', json.dumps(report))
            for data in ('{private-token', '[]', '{"version":true,"issues":{}}',
                         json.dumps(receipt('2026-11-12T12:00:01Z')),
                         json.dumps(receipt('2026-02-30T12:00:00Z')),
                         json.dumps(receipt('/private/path'))):
                path.write_text(data)
                with patch.object(watcher.time, 'time', return_value=now):
                    report = watcher.status_report()
                self.assertEqual(report['diagnostics']['status'], 'unavailable')
                self.assertIsNone(report['diagnostics']['scoped_blocked_count'])
                self.assertIsNone(report['last_coordinator']['exit_status'])
            path.unlink()
            target = Path(folder) / 'secret'
            target.write_text(json.dumps(receipt('2026-11-12T11:59:00Z')))
            target.chmod(0o600)
            if os.name != 'nt':
                path.symlink_to(target)
                self.assertEqual(watcher.status_report()['diagnostics']['status'], 'unavailable')

    def test_actual_cli_is_read_only_private_and_format_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            state = home / 'state'
            state.mkdir(mode=0o700)
            path = state / watcher.RUN_STATE
            env = {key: value for key, value in os.environ.items() if key in ('SystemRoot', 'WINDIR')}
            env.update(HOME=folder, USERPROFILE=folder, PATH='', VEZRYN_GRAPH_STATE=str(state),
                       VEZRYN_GRAPH_CONFIG=str(home / 'missing.toml'), PYTHONDONTWRITEBYTECODE='1')
            for data in (None, receipt(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())),
                         {'version': 1, 'issues': 'private-token'}):
                if data is not None:
                    path.write_text(json.dumps(data))
                    path.chmod(0o600)
                before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in state.iterdir()}
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'status', '--json'],
                                        env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['schema_version'], 1)
                self.assertEqual(report['live_workers'], 'unknown')
                self.assertEqual(report['source_identity']['status'], 'unavailable')
                self.assertNotIn(folder, result.stdout + result.stderr)
                self.assertNotIn('private-token', result.stdout + result.stderr)
                self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in state.iterdir()}, before)
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'status', '--json', '--details'],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)

    def test_existing_formats_are_preserved(self):
        state = {'version': 1, 'issues': {}, 'pending': None, 'hold': None}
        source = {'status': 'verified', 'evidence': {}}
        with patch.object(watcher, 'load_run_state', return_value=state), \
             patch.object(watcher, 'activation_source', return_value=source):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                watcher.run_status(details=True)
            self.assertEqual(output.getvalue(), json.dumps(state, indent=2, sort_keys=True) + '\n')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                watcher.run_status()
            self.assertTrue(output.getvalue().startswith('Graph current local source: verified;'))
            self.assertIn('Graph scoped diagnostics: 0 total;', output.getvalue())

    @unittest.skipIf(os.name == 'nt', 'Linux shell entry point')
    def test_shell_entry_point_emits_only_json_without_service_probe(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            trap = home / 'systemctl'
            trap.write_text('#!/bin/sh\necho forbidden-service-probe >&2\nexit 99\n')
            trap.chmod(0o755)
            env = dict(os.environ, HOME=folder, VEZRYN_GRAPH_STATE=str(home / 'missing'),
                       PATH=folder + os.pathsep + os.defpath, PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run(['bash', str(ROOT / 'bin/graph'), 'status', '--json'],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(json.loads(result.stdout)['diagnostics']['status'], 'missing')
            self.assertFalse((home / 'missing').exists())


if __name__ == '__main__':
    unittest.main()
