"""Offline queue integration: injected gh metadata, isolated config, no user account."""
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


def issue(number=1, labels=('status:ready',)):
    return {'number': number, 'updatedAt': '2026-11-12T10:00:00Z',
            'labels': [{'name': label} for label in labels]}


class QueueTests(unittest.TestCase):
    def test_candidates_and_dispatch_filter_share_metadata_source(self):
        response = [issue(), issue(2, ('status:ready', 'status:blocked')), issue(3, ('other',))]
        with patch.object(watcher, 'enrolled', return_value=['example/project']), \
             patch.object(watcher.platform, 'executable', return_value='fake-gh'), \
             patch.object(watcher.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, json.dumps(response))) as run:
            report = watcher.queue_report()
            self.assertTrue(report['complete'])
            entry = report['repositories'][0]
            self.assertEqual([i['number'] for i in entry['candidates']], [1, 2])
            self.assertIn('status:blocked', entry['candidates'][1]['lifecycle_labels'])
            self.assertTrue(all(i['classification'] == 'READY_LABEL_CANDIDATE' for i in entry['candidates']))
            self.assertGreaterEqual(entry['source_age_seconds'], 0)
            self.assertEqual(watcher.backlog(['example/project']),
                             ([{'repo': 'example/project', 'number': 1, 'updatedAt': response[0]['updatedAt']}], 0))
            for call in run.call_args_list:
                self.assertEqual(call.args[0], ['fake-gh', 'issue', 'list', '--repo', 'example/project',
                    '--state', 'open', '--label', 'status:ready', '--limit', '1000', '--json', 'number,updatedAt,labels'])

    def test_partial_failure_cap_and_invalid_response(self):
        for failed in (FileNotFoundError('secret-path'), subprocess.CalledProcessError(1, ['secret-token']),
                       subprocess.TimeoutExpired('secret-path', 60), subprocess.CompletedProcess([], 0, '{}'),
                       subprocess.CompletedProcess([], 0, json.dumps([issue(), {'number': 2}]))):
            good = subprocess.CompletedProcess([], 0, json.dumps([issue()]))
            with patch.object(watcher, 'enrolled', return_value=['example/one', 'example/two']), \
                 patch.object(watcher.platform, 'executable', return_value='fake-gh'), \
                 patch.object(watcher.subprocess, 'run', side_effect=[good, failed]):
                report = watcher.queue_report()
                self.assertFalse(report['complete'])
                self.assertEqual([r['status'] for r in report['repositories']], ['complete', 'failed'])
                self.assertEqual(report['repositories'][1]['candidates'], [])
                self.assertNotIn('secret', json.dumps(report))
        with patch.object(watcher, 'enrolled', return_value=['example/project']), \
             patch.object(watcher, 'ready_metadata', return_value=[issue(n) for n in range(1, 1001)]):
            report = watcher.queue_report()
            self.assertFalse(report['complete'])
            self.assertEqual(report['repositories'][0]['status'], 'incomplete')
            self.assertEqual(len(report['repositories'][0]['candidates']), 1000)

    def test_explanation_observations_and_fail_closed_reads(self):
        def conn(nodes=(), complete=True):
            return {'nodes': list(nodes), 'totalCount': len(nodes),
                    'pageInfo': {'hasNextPage': not complete}}

        def snapshot():
            return {'number': 1, 'state': 'OPEN', 'updatedAt': issue()['updatedAt'],
                    'body': '', 'labels': conn([{'name': 'status:ready'}]),
                    'comments': conn(), 'blockedBy': conn(),
                    'closedByPullRequestsReferences': conn()}

        cases = [('candidate', 'NO_OBSERVED_BLOCKER', lambda raw: None),
            ('blocked', 'CONFLICTING_LIFECYCLE_LABELS', lambda raw: raw.update(
                labels=conn([{'name': 'status:ready'}, {'name': 'status:blocked'}]))),
            ('blocked', 'OPEN_CLOSING_PR', lambda raw: raw.update(
                closedByPullRequestsReferences=conn([{'state': 'OPEN', 'url': 'https://github.com/example/project/pull/2'}]))),
            ('blocked', 'OPEN_DEPENDENCY', lambda raw: raw.update(
                blockedBy=conn([{'state': 'OPEN', 'url': 'https://github.com/example/project/issues/2'}]))),
            ('unknown', 'CLAIM_REQUIRES_RECONCILIATION', lambda raw: raw.update(
                comments=conn([{'body': 'Graph claimed — secret /private/path native-id'}]))),
            ('unknown', 'COMMENTS_INCOMPLETE', lambda raw: raw.update(comments=conn(complete=False))),
            ('unknown', 'DEPENDENCY_READ_INCOMPLETE', lambda raw: raw.update(blockedBy=conn(complete=False))),
            ('unknown', 'STALE_CANDIDATE', lambda raw: raw.update(updatedAt='old')),
            ('unknown', 'RELATED_SCOPE_UNAVAILABLE', lambda raw: raw.update(
                body='Blocked by https://github.com/private/other/issues/2')),
            ('unknown', 'DEPENDENCY_INTENT_MISMATCH', lambda raw: raw.update(
                body='<!-- graph-dependencies -->\nNone\n<!-- /graph-dependencies -->',
                blockedBy=conn([{'state': 'CLOSED', 'url': 'https://github.com/example/project/issues/2'}])))]
        for classification, reason, mutate in cases:
            with self.subTest(reason=reason):
                raw = snapshot()
                mutate(raw)
                with patch.object(watcher, 'enrolled', return_value=['example/project']), \
                     patch.object(watcher, 'ready_metadata', return_value=[issue()]), \
                     patch.object(watcher, 'dependency_query', return_value={'repository': {'issue': raw}}):
                    report = watcher.queue_report(explain=True)
                detail = report['repositories'][0]['candidates'][0]['explanation']
                self.assertEqual(detail['classification'], classification)
                self.assertIn(reason, detail['reasons'])
                self.assertIsNotNone(detail['observed_at'])
                self.assertNotIn('secret', json.dumps(report))
                self.assertNotIn('private/other', json.dumps(report))
        for error, reason in [(watcher.NativeDependencyUnsupported(), 'API_CAPABILITY_UNAVAILABLE'),
                              (subprocess.CalledProcessError(1, ['secret'], stderr='rate limit denied secret'), 'SNAPSHOT_UNAVAILABLE')]:
            with patch.object(watcher, 'enrolled', return_value=['example/project']), \
                 patch.object(watcher, 'ready_metadata', return_value=[issue()]), \
                 patch.object(watcher, 'dependency_query', side_effect=error):
                report = watcher.queue_report(explain=True)
                self.assertFalse(report['complete'])
                self.assertEqual(report['repositories'][0]['candidates'][0]['explanation']['reasons'], [reason])
                self.assertNotIn('secret', json.dumps(report))

    def test_explanation_bounds_related_reads_and_no_enrollment(self):
        def conn(nodes=()):
            return {'nodes': list(nodes), 'totalCount': len(nodes), 'pageInfo': {'hasNextPage': False}}
        def query(*args, **kwargs):
            n = kwargs['number']
            return {'repository': {'issue': {'number': n, 'state': 'OPEN', 'updatedAt': issue()['updatedAt'],
                'body': 'Blocked by https://github.com/example/project/issues/99',
                'labels': conn([{'name': 'status:ready'}]), 'comments': conn(),
                'blockedBy': conn(), 'closedByPullRequestsReferences': conn()}}}
        with patch.object(watcher, 'enrolled', return_value=['example/project']), \
             patch.object(watcher, 'ready_metadata', return_value=[issue(n) for n in range(1, 23)]), \
             patch.object(watcher, 'dependency_query', side_effect=query) as read, \
             patch.object(watcher, 'github', return_value={'state': 'OPEN'}) as related:
            report = watcher.queue_report(explain=True)
            self.assertEqual(read.call_count, 20)
            self.assertEqual(related.call_count, 20)
            self.assertEqual(report['repositories'][0]['candidates'][-1]['explanation']['reasons'], ['CANDIDATE_READ_CAP'])
            self.assertIn('OPEN_DEPENDENCY', report['repositories'][0]['candidates'][0]['explanation']['reasons'])
            self.assertFalse(report['complete'])
        with patch.object(watcher, 'enrolled', return_value=[]), patch.object(watcher, 'github') as read:
            self.assertTrue(watcher.queue_report(explain=True)['complete'])
            read.assert_not_called()

    @unittest.skipIf(os.name == 'nt', 'Synthetic POSIX executable; not native Windows qualification')
    def test_actual_cli_fake_gh_and_temporary_config_no_writes(self):
        with tempfile.TemporaryDirectory(prefix='Community queue spaces ') as folder:
            home = Path(folder)
            config = home / 'repos.toml'
            config.write_text('repositories = ["example/one", "example/two"]')
            config.chmod(0o600)
            gh = home / 'gh'
            gh.write_text('#!' + sys.executable + '\nimport json, sys\n'
                          'assert sys.argv[1:4] == ["issue", "list", "--repo"]\n'
                          'assert sys.argv[5:] == ["--state", "open", "--label", "status:ready", "--limit", "1000", "--json", "number,updatedAt,labels"]\n'
                          'print(json.dumps(' + repr([issue()]) + '))\n')
            gh.chmod(0o755)
            env = {key: value for key, value in os.environ.items() if key in ('SystemRoot', 'WINDIR')}
            env.update(HOME=folder, USERPROFILE=folder, PATH=folder, VEZRYN_GRAPH_CONFIG=str(config),
                       VEZRYN_GRAPH_STATE=str(home / 'state'), PYTHONDONTWRITEBYTECODE='1')
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in home.iterdir()}
            for options in ([], ['--json']):
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'queue', *options],
                                        env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(folder, result.stdout + result.stderr)
                self.assertIn('READY_LABEL_CANDIDATE', result.stdout)
                if options:
                    self.assertTrue(json.loads(result.stdout)['complete'])
            # The real CLI explain path receives a bounded, accounts-free GraphQL snapshot.
            connection = lambda nodes: {'nodes': nodes, 'totalCount': len(nodes), 'pageInfo': {'hasNextPage': False}}
            raw = {'number': 1, 'state': 'OPEN', 'updatedAt': issue()['updatedAt'], 'body': '',
                   'labels': connection([{'name': 'status:ready'}]), 'comments': connection([]),
                   'blockedBy': connection([]), 'closedByPullRequestsReferences': connection([])}
            original = gh.read_text()
            gh.write_text(original.replace('assert sys.argv[1:4]',
                'if sys.argv[1:3] == ["api", "graphql"]:\n print(' + repr(json.dumps({'data': {'repository': {'issue': raw}}})) + ')\n sys.exit(0)\nassert sys.argv[1:4]'))
            for options in (['--explain'], ['--explain', '--json']):
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'queue', *options],
                                        env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('NO_OBSERVED_BLOCKER', result.stdout)
                self.assertNotIn(folder, result.stdout + result.stderr)
            gh.write_text(original)
            # Restore only this test-owned fixture's mtime for the read-only assertion.
            os.utime(gh, ns=(gh.stat().st_atime_ns, before['gh'][1]))
            self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in home.iterdir()}, before)
            for contents in ('repositories = ["example/one", "EXAMPLE/one"]', 'invalid secret'):
                config.write_text(contents)
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'queue', '--json'],
                                        env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)['configuration'], 'unavailable')
                self.assertNotIn(folder, result.stdout + result.stderr)
            config.write_text('repositories = ["example/one"]')
            gh.unlink()
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'queue', '--json'],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['repositories'][0]['status'], 'failed')
            config.unlink()
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'watcher.py'), 'queue'],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0)
            self.assertIn('No enrolled repositories', result.stdout)
            self.assertFalse(config.exists())


if __name__ == '__main__':
    unittest.main()
