"""Offline routing: Linux subprocesses and platform-isolated Python wrappers.

Platform-name mocks exercise argument routing, not native macOS/Windows services.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def entrypoint(name, root=ROOT):
    if name == 'linux':
        return ['/bin/bash', str(root / 'bin/graph')]
    # Only platform detection is mocked; forwarding invokes a real subprocess.
    return [sys.executable, '-B', '-c',
            'import sys; from pathlib import Path; from unittest.mock import patch; '
            f'import graph_{name} as runner; runner.ROOT = Path({str(root)!r}); '
            f'platform = patch.object(runner.platform, "platform_name", return_value={name!r}); '
            'platform.start(); sys.argv = ["graph", *sys.argv[1:]]; raise SystemExit(runner.main())']


class EntrypointTests(unittest.TestCase):
    def names(self):
        return ('linux', 'macos', 'windows') if sys.platform.startswith('linux') else ('macos', 'windows')

    def env(self, home):
        env = {k: v for k, v in os.environ.items() if k in ('PATH', 'SystemRoot', 'WINDIR', 'TEMP', 'TMP')}
        env.update(HOME=str(home), USERPROFILE=str(home), LOCALAPPDATA=str(home / 'local'),
                   VEZRYN_GRAPH_CONFIG=str(home / 'repos.toml'), VEZRYN_GRAPH_STATE=str(home / 'state'),
                   VEZRYN_GRAPH_LIBRARY=str(home / 'library'), PYTHONDONTWRITEBYTECODE='1')
        return env

    def run_cli(self, command, args, env):
        return subprocess.run([*command, *args], cwd=ROOT, env=env, capture_output=True, timeout=10)

    def test_exact_arguments_stdout_stderr_and_exit_codes(self):
        with tempfile.TemporaryDirectory(prefix='Community forwarding ') as folder:
            root = Path(folder)
            (root / 'bin').mkdir()
            shutil.copyfile(ROOT / 'bin/graph', root / 'bin/graph')
            (root / 'watcher.py').write_text(
                'import json, os, sys\n'
                'print(json.dumps(sys.argv[1:]), flush=True)\n'
                'print("underlying diagnostic", file=sys.stderr)\n'
                'raise SystemExit(int(os.environ["TEST_EXIT"]))\n')
            env = self.env(root)
            commands = (['doctor'], ['doctor', '--json'], ['queue'], ['queue', '--json'],
                        ['library'], ['library', '--explain'], ['repo', 'check', '--json'],
                        ['repo', 'check', 'example/project', '--json'])
            for name in self.names():
                for args in commands:
                    for code in (0, 1, 7):
                        with self.subTest(platform=name, args=args, code=code):
                            env['TEST_EXIT'] = str(code)
                            result = self.run_cli(entrypoint(name, root), args, env)
                            self.assertEqual(result.returncode, code, result.stderr)
                            self.assertEqual(result.stdout, (json.dumps(args) + '\n').encode())
                            self.assertEqual(result.stderr, b'underlying diagnostic\n')

    def test_real_watcher_diagnostics_and_visible_invalid_flags(self):
        with tempfile.TemporaryDirectory(prefix='Community diagnostics ') as folder:
            home = Path(folder)
            env = self.env(home)
            if os.name != 'nt':
                tools = home / 'tools'
                tools.mkdir()
                for tool in ('systemctl', 'launchctl', 'powershell', 'gh', 'codex'):
                    executable = tools / tool
                    executable.write_text('#!' + sys.executable + '\nfrom pathlib import Path\n'
                                          + 'Path(' + repr(str(home / 'unexpected-probe')) + ').touch()\n'
                                          + 'raise SystemExit(99)\n')
                    executable.chmod(0o755)
                env['PATH'] = str(tools) + os.pathsep + env.get('PATH', '')
            # Empty enrollment is an accounts-free successful queue. Invalid
            # enrollment fails before any GitHub read, exercising real failures.
            for config in (None, 'invalid private configuration'):
                if config is not None:
                    (home / 'repos.toml').write_text(config)
                for args in (['doctor', '--json'], ['queue', '--json'], ['library', '--explain']):
                    baseline = self.run_cli([sys.executable, '-B', str(ROOT / 'watcher.py')], args, env)
                    for name in self.names():
                        with self.subTest(platform=name, args=args, config=config):
                            result = self.run_cli(entrypoint(name), args, env)
                            self.assertEqual(result.returncode, baseline.returncode, result.stderr)
                            actual, expected = json.loads(result.stdout), json.loads(baseline.stdout)
                            if args[0] == 'queue':
                                actual.pop('generated_at')
                                expected.pop('generated_at')
                            self.assertEqual(actual, expected)
                            self.assertEqual(result.stderr, baseline.stderr)
                self.assertFalse((home / 'state').exists())
                self.assertFalse((home / 'library').exists())
                self.assertFalse((home / 'unexpected-probe').exists())
            for name in self.names():
                for command in ('doctor', 'queue', 'library'):
                    result = self.run_cli(entrypoint(name), [command, '--unknown-flag'], env)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn(b'--unknown-flag', result.stderr)
                    self.assertFalse(result.stdout)
                help_result = self.run_cli(entrypoint(name), ['--help'], env)
                for command in (b'doctor', b'queue', b'library'):
                    self.assertIn(command, help_result.stdout)


if __name__ == '__main__':
    unittest.main()
