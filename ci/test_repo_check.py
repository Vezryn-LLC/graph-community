"""Repository preflight with offline fake gh only; no account or dispatch."""
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

META = dict(full_name='example/project', private=False, archived=False, disabled=False, has_issues=True)
LABELS = [{'name': label} for label in watcher.LIFECYCLE_LABELS]


class RepoCheckTests(unittest.TestCase):
    def report(self, responses):
        with patch.object(watcher.platform, 'executable', return_value='fake-gh'), \
             patch.object(watcher.subprocess, 'run', side_effect=[
                 subprocess.CompletedProcess([], 0, json.dumps(r)) if not isinstance(r, Exception) else r
                 for r in responses]) as run:
            report = watcher.repo_check_report('example/project')
            for call in run.call_args_list:
                self.assertEqual(call.args[0][:4], ['fake-gh', 'api', '--method', 'GET'])
                self.assertTrue(call.args[0][4].startswith('repos/example/project'))
            return report, run

    def test_metadata_labels_and_permissions(self):
        report, _ = self.report([META | {'permissions': {'pull': True, 'push': False, 'admin': 'secret'}}, LABELS])
        self.assertTrue(report['complete'])
        entry = report['repositories'][0]
        self.assertEqual(entry['status'], 'configured_readable')
        self.assertEqual(entry['metadata']['reported_permissions'], {'pull': True, 'push': False})
        report, _ = self.report([META, LABELS[:1]])
        self.assertEqual(report['repositories'][0]['labels']['status:blocked'], 'missing')
        self.assertFalse(report['complete'])

    def test_failures_are_separate_and_sanitized(self):
        for failure, status in [
            (subprocess.CalledProcessError(1, ['secret'], stderr='token-secret HTTP 403'), 'access_denied'),
            (subprocess.CalledProcessError(1, ['secret'], stderr='HTTP 403 API rate limit exceeded secret'), 'rate_limited'),
            (subprocess.CalledProcessError(1, ['secret'], stderr='HTTP 404 secret'), 'unavailable_or_not_found'),
            (FileNotFoundError('secret'), 'unavailable'),
            (subprocess.TimeoutExpired('secret', 60), 'timeout'),
            ({'secret': True}, 'invalid_response'),
        ]:
            for responses in ([failure, LABELS], [META, failure]):
                report, _ = self.report(responses)
                entry = report['repositories'][0]
                field = 'metadata' if responses[0] is failure else 'label_read'
                self.assertEqual(entry[field]['status'], status)
                self.assertEqual(entry['status'], 'read_failed')
                self.assertNotIn('secret', json.dumps(report))
                if field == 'label_read':
                    self.assertEqual(set(entry['labels'].values()), {'unknown'})

    def test_pagination_and_bound(self):
        page = [{'name': f'other-{n}'} for n in range(100)]
        report, run = self.report([META, page, LABELS])
        self.assertTrue(report['complete'])
        self.assertTrue(run.call_args_list[-1].args[0][-1].endswith('page=2'))
        report, run = self.report([META] + [page] * 10)
        self.assertEqual(run.call_count, 11)
        entry = report['repositories'][0]
        self.assertEqual(entry['label_read']['status'], 'incomplete')
        self.assertEqual(set(entry['labels'].values()), {'unknown'})

    def test_targets_config_and_no_dispatch(self):
        with patch.object(watcher, 'enrolled', return_value=[]) as enrolled, \
             patch.object(watcher, 'github', side_effect=AssertionError('unexpected read')), \
             patch.object(watcher, 'launch', side_effect=AssertionError('dispatch')), \
             patch.object(watcher, 'save', side_effect=AssertionError('write')):
            self.assertEqual(watcher.repo_check_report()['repositories'], [])
            self.assertFalse(watcher.repo_check_report('--bad')['complete'])
            self.assertEqual(enrolled.call_count, 1)
        with patch.object(watcher, 'enrolled', side_effect=ValueError('secret')):
            report = watcher.repo_check_report()
            self.assertFalse(report['complete'])
            self.assertNotIn('secret', json.dumps(report))

    @unittest.skipIf(os.name == 'nt', 'Synthetic POSIX executable, not native qualification')
    def test_cli_fake_gh_no_state_writes(self):
        with tempfile.TemporaryDirectory(prefix='repo check ') as folder:
            home = Path(folder)
            gh = home / 'gh'
            gh.write_text('#!' + sys.executable + '\nimport json, sys\n'
                          'assert sys.argv[1:4] == ["api", "--method", "GET"]\n'
                          'endpoint = sys.argv[4]\n'
                          'assert endpoint in ["repos/example/project", "repos/example/project/labels?per_page=100&page=1"]\n'
                          'print(json.dumps(' + repr(META) + ' if endpoint == "repos/example/project" else ' + repr(LABELS) + '))\n')
            gh.chmod(0o755)
            config = home / 'repos.toml'
            config.write_text('repositories = ["example/project"]')
            config.chmod(0o600)
            env = dict(HOME=folder, PATH=folder, VEZRYN_GRAPH_CONFIG=str(config),
                       VEZRYN_GRAPH_STATE=str(home / 'state'), PYTHONDONTWRITEBYTECODE='1')
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in home.iterdir()}
            for args in (['example/project'], ['--json'], ['example/project', '--json']):
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'repo', 'check', *args],
                                        env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('configured_readable', result.stdout)
                self.assertNotIn(folder, result.stdout + result.stderr)
            self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in home.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
