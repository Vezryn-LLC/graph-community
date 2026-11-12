"""Isolated enrollment transactions; no network, worker or service operations."""
import contextlib
import io
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


class EnrollmentTests(unittest.TestCase):
    def test_two_process_edits_do_not_lose_successful_changes(self):
        cases = [([], ('add', 'example/two'), ['example/one', 'example/two']),
                 (['example/keep', 'example/revoked'], ('revoke', 'EXAMPLE/revoked'),
                  ['example/keep', 'example/one'])]
        for initial, second, expected in cases:
            with self.subTest(second=second), tempfile.TemporaryDirectory(prefix='Community enrollment ') as folder:
                home = Path(folder)
                config, ready = home / 'config/repos.toml', home / 'read-ready'
                with patch.object(watcher, 'CONFIG', config):
                    watcher.save(initial)
                env = dict(os.environ, VEZRYN_GRAPH_CONFIG=str(config),
                           VEZRYN_GRAPH_STATE=str(home / 'state'), PYTHONDONTWRITEBYTECODE='1')
                # Pause the first real process immediately after its read. The
                # contender must either fail before reading or preserve both edits.
                code = '''import pathlib, sys, watcher
original = watcher.enrolled
def paused():
    result = original()
    pathlib.Path(sys.argv[1]).touch()
    if sys.stdin.readline() != "continue\\n":
        raise RuntimeError("Test writer interrupted")
    return result
watcher.enrolled = paused
watcher.manage("add", "example/one")
'''
                first = subprocess.Popen([sys.executable, '-B', '-c', code, str(ready)],
                                         cwd=ROOT, env=env, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 5
                    while not ready.exists() and first.poll() is None and time.monotonic() < deadline:
                        time.sleep(.01)
                    self.assertTrue(ready.exists(), 'First writer did not reach the controlled read')
                    contender = subprocess.run([sys.executable, '-B', 'watcher.py', 'repo', *second],
                                               cwd=ROOT, env=env, capture_output=True, text=True, timeout=5)
                    stdout, stderr = first.communicate('continue\n', timeout=5)
                    self.assertEqual(first.returncode, 0, stdout + stderr)
                    self.assertIn(contender.returncode, (0, 1), contender.stderr)
                    if contender.returncode:
                        self.assertIn('retry', contender.stderr.lower())
                        self.assertNotIn('revoke:', contender.stdout)
                        subprocess.run([sys.executable, '-B', 'watcher.py', 'repo', *second],
                                       cwd=ROOT, env=env, check=True, capture_output=True, timeout=5)
                    with patch.object(watcher, 'CONFIG', config):
                        self.assertEqual(watcher.enrolled(), expected)
                    # Existing case-insensitive idempotence remains unchanged.
                    subprocess.run([sys.executable, '-B', 'watcher.py', 'repo', 'add', 'EXAMPLE/ONE'],
                                   cwd=ROOT, env=env, check=True, capture_output=True, timeout=5)
                    with patch.object(watcher, 'CONFIG', config):
                        self.assertEqual(watcher.enrolled(), expected)
                finally:
                    if first.poll() is None:
                        first.kill()  # Only this test's child; never a runtime process.
                        first.communicate(timeout=5)

    def test_failed_replace_preserves_config_and_only_cleans_owned_temp(self):
        with tempfile.TemporaryDirectory(prefix='Community interrupted enrollment ') as folder:
            config = Path(folder) / 'config/repos.toml'
            with patch.object(watcher, 'CONFIG', config), contextlib.redirect_stdout(io.StringIO()):
                watcher.save(['example/keep'])
                before = config.read_bytes()
                unrelated = config.parent / 'unrelated.tmp'
                unrelated.write_text('retain')
                for failure in (OSError('injected replacement failure'), KeyboardInterrupt()):
                    with patch.object(watcher.os, 'replace', side_effect=failure):
                        with self.assertRaises(type(failure)):
                            watcher.manage('add', 'example/new')
                    self.assertEqual(config.read_bytes(), before)
                    self.assertEqual(unrelated.read_text(), 'retain')
                    self.assertEqual(list(config.parent.glob('*.tmp')), [unrelated])
                # A colliding file was not created by this invocation: preserve it.
                collision = config.with_name(config.name + f'.{os.getpid()}.tmp')
                collision.write_text('also retain')
                if os.name != 'nt':
                    collision.chmod(0o600)
                with self.assertRaises(FileExistsError):
                    watcher.manage('add', 'example/new')
                self.assertEqual(collision.read_text(), 'also retain')
                self.assertEqual(config.read_bytes(), before)
                collision.unlink()
                watcher.manage('add', 'example/new')  # Failure released ownership.
                self.assertEqual(watcher.enrolled(), ['example/keep', 'example/new'])
                if os.name != 'nt':
                    self.assertEqual(config.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(config.with_name(config.name + '.lock').stat().st_mode & 0o777, 0o600)

    def test_list_and_invalid_name_do_not_create_state(self):
        with tempfile.TemporaryDirectory(prefix='Community enrollment list ') as folder:
            config = Path(folder) / 'absent/repos.toml'
            with patch.object(watcher, 'CONFIG', config), contextlib.redirect_stdout(io.StringIO()):
                watcher.manage('list', None)
                with self.assertRaises(ValueError):
                    watcher.manage('add', 'invalid')
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
