"""Offline preflight checks: no client execution, credentials or state writes."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import watcher


class DoctorTests(unittest.TestCase):
    def test_actual_cli_missing_tools_and_no_writes(self):
        with tempfile.TemporaryDirectory(prefix='Community doctor spaces ') as folder:
            home = Path(folder)
            env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                       LOCALAPPDATA=str(home / 'local'), PATH='',
                       VEZRYN_GRAPH_CONFIG=str(home / 'config/repos.toml'),
                       VEZRYN_GRAPH_STATE=str(home / 'state'),
                       VEZRYN_GRAPH_LIBRARY=str(home / 'library'))
            for option in ([], ['--json']):
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'doctor', *option],
                                        env=env, capture_output=True, text=True, check=True, timeout=10)
                self.assertEqual(list(home.rglob('*')), [])
                self.assertNotIn(str(home), result.stdout + result.stderr)
                if option:
                    report = json.loads(result.stdout)
                    self.assertEqual(report['prerequisites'], {'git': False, 'gh': False, 'codex': False})
                    self.assertEqual(report['native_codex']['status'], 'unavailable')
                    self.assertEqual(report['configuration']['status'], 'not_configured')
                    self.assertTrue(all(report['library']['required_policies'].values()))
                else:
                    self.assertIn('NOT checked', result.stdout)
            if os.name != 'nt':
                # These executables would leave evidence if preflight invoked one.
                for name in ('git', 'gh', 'codex'):
                    tool = home / name
                    tool.write_text('#!/bin/sh\nprintf called > "' + str(home / 'called') + '"\n')
                    tool.chmod(0o755)
                before = {path.name: path.read_bytes() for path in home.iterdir()}
                env['PATH'] = str(home)
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'doctor', '--json'],
                                        env=env, capture_output=True, text=True, check=True, timeout=10)
                report = json.loads(result.stdout)
                self.assertTrue(all(report['prerequisites'].values()))
                self.assertEqual(report['native_codex']['status'], 'unavailable')
                self.assertEqual({path.name: path.read_bytes() for path in home.iterdir()}, before)

    @unittest.skipIf(os.name == 'nt', 'POSIX owner/mode fixture; Windows DACL qualification remains separate')
    def test_config_count_and_redacted_negative_cases(self):
        with tempfile.TemporaryDirectory(prefix='Community config ') as folder:
            config = Path(folder) / 'repos.toml'
            with patch.object(watcher, 'CONFIG', config), patch.object(watcher.platform, 'native_codex', side_effect=FileNotFoundError), \
                 patch.object(watcher.subprocess, 'run', side_effect=AssertionError('No subprocess allowed')):
                for contents, expected in [('repositories = ["example/project"]', 'available'),
                                           ('repositories = ["example/project", "EXAMPLE/project"]', 'unknown'),
                                           ('repositories = "private-value"', 'unknown'),
                                           ('invalid secret content', 'unknown')]:
                    config.write_text(contents)
                    config.chmod(0o600)
                    before = config.read_bytes(), config.stat().st_mtime_ns
                    report = watcher.doctor()
                    self.assertEqual(report['configuration']['status'], expected)
                    self.assertEqual(report['configuration']['repository_count'], 1 if expected == 'available' else None)
                    self.assertNotIn('private-value', json.dumps(report))
                    self.assertNotIn(str(config), json.dumps(report))
                    self.assertEqual((config.read_bytes(), config.stat().st_mtime_ns), before)
                if os.name != 'nt':
                    config.chmod(0o644)
                    self.assertEqual(watcher.doctor()['configuration']['status'], 'unknown')
                    config.unlink()
                    config.symlink_to(Path(folder) / 'missing')
                    self.assertEqual(watcher.doctor()['configuration']['status'], 'unknown')

    @unittest.skipIf(os.name == 'nt', 'Synthetic POSIX launcher, not Windows qualification')
    def test_unsupported_wrapper_and_native_resolution_without_execution(self):
        with tempfile.TemporaryDirectory(prefix='Community tools ') as folder:
            launcher = Path(folder) / 'codex'
            with patch.dict(os.environ, {'PATH': folder}), \
                 patch.object(watcher.subprocess, 'run', side_effect=AssertionError('No subprocess allowed')):
                launcher.write_text('#!/bin/sh\nexit 99\n')
                launcher.chmod(0o755)
                self.assertTrue(watcher.doctor()['prerequisites']['codex'])
                self.assertEqual(watcher.doctor()['native_codex']['status'], 'unavailable')
                magic = b'\x7fELF' if watcher.platform.platform_name() == 'linux' else b'\xfe\xed\xfa\xce'
                launcher.write_bytes(magic)
                self.assertEqual(watcher.doctor()['native_codex']['status'], 'available')

    def test_library_missing_policy_invalid_override_and_experimental_limits(self):
        with tempfile.TemporaryDirectory(prefix='Community guidance ') as folder:
            overrides = Path(folder) / 'library'
            overrides.mkdir()
            marker = overrides / 'policies/ENGINEERING.md.disabled'
            marker.parent.mkdir()
            marker.touch()
            with patch.dict(os.environ, {'VEZRYN_GRAPH_LIBRARY': str(overrides)}):
                report = watcher.doctor()
                self.assertEqual(report['library']['status'], 'unavailable')
                self.assertFalse(report['library']['required_policies']['ENGINEERING'])
            with patch.dict(os.environ, {'VEZRYN_GRAPH_LIBRARY': str(marker)}):
                self.assertEqual(watcher.doctor()['library']['status'], 'unknown')
            capabilities = watcher.platform.capabilities()
            capabilities['qualification'] = 'experimental-unverified'
            with patch.object(watcher.platform, 'capabilities', return_value=capabilities):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    watcher.print_doctor()
                self.assertIn('experimental-unverified', output.getvalue())
                self.assertIn('native-host qualification NOT checked', output.getvalue())


if __name__ == '__main__':
    unittest.main()
