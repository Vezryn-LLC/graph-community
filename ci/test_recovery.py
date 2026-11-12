"""Synthetic post-handoff chronology and restart checks; no native worker or account."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import watcher

KEY = 'example/project#1'
PARENT = 'example/project#2'
REPOSITORIES = ['example/project']


def connection(nodes):
    return {'totalCount': len(nodes), 'pageInfo': {'hasNextPage': False, 'hasPreviousPage': False},
            'nodes': nodes}


def comment(body, at='2026-11-10T10:00:00Z'):
    return {'body': body, 'url': 'https://github.com/example/project/issues/1#issuecomment-1',
            'createdAt': at}


def event(at='2026-11-10T11:00:00Z', epoch='ready-new'):
    return {'__typename': 'LabeledEvent', 'id': epoch, 'createdAt': at,
            'label': {'name': 'status:ready'}}


def source():
    return {'number': 1, 'state': 'OPEN', 'body': '',
            'labels': connection([{'name': 'status:ready'}]),
            'comments': connection([comment('Graph retirement pending\nWorker: sample-worker\n'
                                           'Worktree: withheld (private local custody)')]),
            'timelineItems': connection([event()]), 'blockedBy': connection([]),
            'closedByPullRequestsReferences': connection([])}


def state(epoch=None):
    return {'version': 1, 'pending': None, 'hold': None, 'issues': {KEY: {
        'issue': KEY, 'ready_epoch': epoch, 'quarantined': True,
        'observation': {'disposition': 'retirement_handoff_unresolved', 'ready_epoch': epoch},
        'last_checked': '2026-11-10T09:00:00Z', 'next_action': 'Preserve source',
        'coordinator_session': 'synthetic-session', 'exit_status': 0, 'parent_scope': None}}}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='Community recovery ')
        self.addCleanup(self.directory.cleanup)
        self.enterContext(patch.object(watcher, 'STATE', Path(self.directory.name)))
        self.enterContext(patch.object(watcher, 'native_session', return_value=None))
        self.enterContext(patch.object(watcher.subprocess, 'run', side_effect=AssertionError('External probe')))

    def refresh(self, current, raw, extra=None):
        observed = {KEY: watcher.source_disposition(raw), **(extra or {})}
        with patch.object(watcher, 'read_dispositions', return_value=observed):
            return watcher.refresh_run_state(current, REPOSITORIES)

    def test_null_baseline_recovers_once_and_restart_preserves_effects(self):
        current, raw = state(), source()
        original = copy.deepcopy(raw)
        watcher.save_run_state(current)
        current = watcher.load_run_state()
        self.assertTrue(self.refresh(current, raw))
        self.assertNotIn(KEY, current['issues'])
        self.assertEqual(raw, original)
        # Persist the existing native launch/reconciliation boundary. No worker is launched.
        observed = watcher.source_disposition(raw)
        current['pending'] = {'issues': [KEY], 'repositories': REPOSITORIES,
                              'before': {KEY: observed}, 'ready_issues': [KEY],
                              'retirements': [KEY], 'exit_status': 0}
        watcher.save_run_state(current)
        current = watcher.load_run_state()
        with patch.object(watcher, 'read_dispositions', return_value={KEY: observed}):
            self.assertFalse(watcher.refresh_run_state(current, REPOSITORIES))
        self.assertEqual(current['issues'][KEY]['ready_epoch'], 'ready-new')
        current = watcher.load_run_state()
        self.assertFalse(self.refresh(current, raw))
        self.assertEqual(current['issues'][KEY]['observation']['disposition'], 'retirement_handoff_unresolved')
        self.assertEqual(current['issues'][KEY]['observation']['retirement'], 'pending')

    def test_nonnull_epoch_behavior_is_unchanged(self):
        raw = source()
        # Existing event-ID transitions do not require the new null-baseline evidence.
        raw['timelineItems']['pageInfo']['hasPreviousPage'] = True
        self.assertTrue(self.refresh(state('ready-old'), raw))
        self.assertFalse(self.refresh(state('ready-new'), raw))
        ordinary = state()
        ordinary['issues'][KEY]['observation']['disposition'] = 'unknown'
        self.assertFalse(self.refresh(ordinary, source()))

    def test_missing_incomplete_malformed_and_old_chronology_stay_held(self):
        cases = []
        for field in ('timelineItems', 'comments'):
            for page_field in ('hasPreviousPage', 'hasNextPage'):
                raw = source()
                raw[field]['pageInfo'][page_field] = True
                cases.append((field + '-' + page_field, raw))
            for missing in ('pageInfo', 'totalCount', 'nodes'):
                raw = source()
                del raw[field][missing]
                cases.append((field + '-missing-' + missing, raw))
            raw = source()
            raw[field]['totalCount'] += 1
            cases.append((field + '-count', raw))
        for stamp in ('2026-11-10T09:00:00Z', '2026-11-10T10:00:00Z',
                      'bad-time', '2026-11-10T11:00:00', None):
            raw = source()
            raw['timelineItems']['nodes'][0]['createdAt'] = stamp
            cases.append(('ready-time-' + str(stamp), raw))
        raw = source()
        raw['timelineItems'] = connection([])
        cases.append(('missing-event', raw))
        raw = source()
        raw['comments'] = connection([])
        cases.append(('missing-handoff', raw))
        raw = source()
        raw['comments']['nodes'][0]['createdAt'] = 'bad-time'
        cases.append(('malformed-handoff', raw))
        raw = source()
        raw['timelineItems']['nodes'][0]['label'] = 'bad-label'
        cases.append(('malformed-label', raw))
        raw = source()
        raw['comments'] = connection([comment('Graph claimed — sample', '2026-11-10T08:00:00Z'),
                                     *raw['comments']['nodes']])
        raw['timelineItems']['nodes'][0]['createdAt'] = None
        cases.append(('claim-with-malformed-event-time', raw))
        raw = source()
        raw['timelineItems'] = connection([event(), event('2026-11-10T09:00:00Z', 'earlier')])
        cases.append(('unordered-events', raw))
        raw = source()
        raw['comments'] = connection([comment('Graph retirement pending'),
                                     comment('Graph retirement pending', '2026-11-10T12:00:00Z')])
        cases.append(('latest-handoff-after-event', raw))
        raw = source()
        raw['timelineItems'] = connection([event(), dict(event('2026-11-10T12:00:00Z', 'removed'),
                                                        __typename='UnlabeledEvent')])
        cases.append(('ready-removed', raw))
        for name, raw in cases:
            with self.subTest(name=name):
                current = state()
                self.assertFalse(self.refresh(current, raw))
                record = current['issues'][KEY]
                self.assertIsNone(record['ready_epoch'])
                self.assertTrue(record['quarantined'])
                self.assertEqual(record['observation']['disposition'], 'retirement_handoff_unresolved')
                self.assertIn('Chronology:', record['next_action'])
                self.assertNotIn('Chronology: verified.', record['next_action'])

    def test_native_ownership_claim_and_parent_holds_are_preserved(self):
        for epoch in (None, 'ready-old'):
            current = state(epoch)
            hold = {'reason': 'unreadable_prior_effects', 'next_action': 'Reconcile ownership'}
            current['hold'] = copy.deepcopy(hold)
            self.assertFalse(self.refresh(current, source()))
            self.assertEqual(current['hold'], hold)
            current = state(epoch)
            current['hold'] = dict(hold, session='synthetic-session')
            with patch.object(watcher, 'ownership_hold', return_value=current['hold']) as ownership:
                self.assertFalse(self.refresh(current, source()))
            ownership.assert_called_once()
            self.assertIn(KEY, current['issues'])
            current = state(epoch)
            current['issues'][KEY]['parent_scope'] = PARENT
            parent_record = copy.deepcopy(current['issues'][KEY])
            parent_record['observation'] = {'disposition': 'unknown'}
            current['issues'][PARENT] = parent_record
            self.assertFalse(self.refresh(current, source(), {PARENT: {'disposition': 'unknown'}}))
            self.assertIn(KEY, current['issues'])
            self.assertIn(PARENT, current['issues'])
        raw = source()
        raw['comments'] = connection([*raw['comments']['nodes'],
            comment('Graph claimed — sample\nWorker: /sample/worker', '2026-11-10T12:00:00Z')])
        self.assertFalse(self.refresh(state(), raw))

    def test_bounded_read_requests_both_completeness_directions(self):
        with patch.object(watcher, 'dependency_query', return_value={'repository': {'i1': source()}}) as query:
            observed = watcher.read_dispositions([KEY])
        self.assertEqual(observed[KEY]['ready_recovery_chronology'], 'verified')
        text = query.call_args.args[0]
        self.assertIn('comments(last:20){totalCount pageInfo{hasNextPage hasPreviousPage', text)
        self.assertIn('timelineItems(last:30,itemTypes:[LABELED_EVENT,UNLABELED_EVENT])', text)
        self.assertIn('pageInfo{hasNextPage hasPreviousPage} totalCount', text)


if __name__ == '__main__':
    unittest.main()
