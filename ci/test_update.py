"""Offline local source identity, including Git and history-free archives."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import graph_update
from ci import check


class VersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = check.check_payload(check.ROOT)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='Version fixture ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'source'
        manifest = json.loads(self.payload['MANIFEST.json'])
        for name, content in self.payload.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(int(manifest['files'][name]['mode'], 8) if name != 'MANIFEST.json' else 0o644)
        self.root_patch = patch.object(graph_update, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args],
                                       text=True, stderr=subprocess.PIPE).strip()

    def test_archive_report_plain_json_and_update_unavailable(self):
        with patch.object(graph_update, 'run', side_effect=AssertionError('unexpected command')):
            value = graph_update.snapshot()
        source = value['source']
        self.assertEqual(value['schema_version'], 1)
        self.assertIsNone(value['release_version'])
        self.assertEqual(value['runtime_identity'], 'unknown')
        self.assertEqual(source, {'kind': 'archive', 'revision': None, 'dirty': None,
                                 'git_state': 'not-present', 'manifest_state': 'verified',
                                 'manifest_sha256': hashlib.sha256(self.payload['MANIFEST.json']).hexdigest()})
        for args in (['version'], ['version', '--json'], ['check-update', '--json']):
            output = io.StringIO()
            with patch.object(sys, 'argv', ['graph_update.py', *args]), contextlib.redirect_stdout(output):
                self.assertEqual(graph_update.main(), 0)
            self.assertNotIn(str(self.root), output.getvalue())
            if '--json' in args:
                self.assertEqual(json.loads(output.getvalue()), value)
            else:
                self.assertIn('dirty: unknown', output.getvalue())
                self.assertIn('Manifest verification: verified', output.getvalue())
        self.assertFalse(value['eligible'])
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            graph_update.activate()

    def test_clean_dirty_git_and_unavailable_git(self):
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture')
        source = graph_update.source_identity()
        self.assertEqual(source['revision'], self.git('rev-parse', 'HEAD'))
        self.assertFalse(source['dirty'])
        self.assertEqual(source['manifest_state'], 'verified')
        (self.root / 'README.md').write_text('modified\n')
        source = graph_update.source_identity()
        self.assertTrue(source['dirty'])
        self.assertEqual(source['manifest_state'], 'invalid')
        with patch.object(graph_update.subprocess, 'run', side_effect=FileNotFoundError('private diagnostic')):
            source = graph_update.source_identity()
        self.assertEqual(source['git_state'], 'unavailable')
        self.assertIsNone(source['revision'])
        self.assertIsNone(source['dirty'])
        self.assertNotIn('private diagnostic', json.dumps(source))

    def test_manifest_missing_corrupt_wrong_shape_and_changed_payload(self):
        manifest = self.root / 'MANIFEST.json'
        manifest.unlink()
        self.assertEqual(graph_update.source_identity()['manifest_state'], 'missing')
        for content in (b'{broken', b'[]', b'{"files": null}'):
            manifest.write_bytes(content)
            source = graph_update.source_identity()
            self.assertEqual(source['manifest_state'], 'invalid')
            self.assertEqual(source['manifest_sha256'], hashlib.sha256(content).hexdigest())
        manifest.write_bytes(self.payload['MANIFEST.json'])
        (self.root / 'README.md').write_text('modified\n')
        self.assertEqual(graph_update.source_identity()['manifest_state'], 'invalid')
        (self.root / 'README.md').write_bytes(self.payload['README.md'])
        broken = b'def broken(\n'
        (self.root / 'graph_update.py').write_bytes(broken)
        value = json.loads(self.payload['MANIFEST.json'])
        value['files']['graph_update.py']['sha256'] = hashlib.sha256(broken).hexdigest()
        manifest.write_text(json.dumps(value))
        self.assertEqual(graph_update.source_identity()['manifest_state'], 'invalid')

    def test_archive_does_not_inherit_parent_git(self):
        subprocess.run(['git', '-C', self.temporary.name, 'init', '-q'], check=True)
        with patch.object(graph_update.subprocess, 'run', side_effect=AssertionError('parent Git queried')):
            self.assertEqual(graph_update.source_identity()['git_state'], 'not-present')


if __name__ == '__main__':
    unittest.main()
