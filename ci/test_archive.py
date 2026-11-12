"""Reproducible source archives and fail-closed payload validation, offline."""
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive
import check


class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = check.check_payload(check.ROOT)

    def copy_source(self, folder):
        source = Path(folder) / 'source'
        source.mkdir()
        for name, content in self.payload.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(archive.modes(self.payload)[name])
        return source

    def test_reproducible_metadata_extraction_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='Archive spaces ') as folder:
            root = Path(folder)
            first, second = root / 'one.tar', root / 'two.tar'
            archive.write_archive(first, self.payload)
            archive.write_archive(second, self.payload)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with tarfile.open(first) as contents:
                self.assertEqual(contents.getnames(), sorted(self.payload))
            extracted = root / 'extracted'
            archive.extract_checked(first, self.payload, extracted)
            self.assertEqual(check.check_payload(extracted), self.payload)
            self.assertIn('not present (archive)', check.check_history(extracted))
            with self.assertRaises(FileExistsError):
                archive.write_archive(first, self.payload)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_extra_member_changed_bytes_and_link_fail_before_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for case in ('extra', 'changed', 'link'):
                path = root / (case + '.tar')
                payload = dict(self.payload)
                if case == 'extra':
                    payload['private-state.txt'] = b'not public'
                    # Deliberately append an unlisted source member to a valid archive.
                    archive.write_archive(path, self.payload)
                    with tarfile.open(path, 'a') as contents:
                        member = tarfile.TarInfo('private-state.txt')
                        member.size = 10
                        contents.addfile(member, io.BytesIO(b'not public'))
                elif case == 'changed':
                    payload['README.md'] += b'\nchanged bytes\n'
                    archive.write_archive(path, payload)
                else:
                    with tarfile.open(path, 'w', format=tarfile.USTAR_FORMAT) as contents:
                        for name in sorted(self.payload):
                            member = tarfile.TarInfo(name)
                            member.mode = archive.modes(self.payload)[name]
                            if name == 'README.md':
                                member.type = tarfile.SYMTYPE
                                member.linkname = 'LICENSE'
                                contents.addfile(member)
                            else:
                                member.size = len(self.payload[name])
                                contents.addfile(member, io.BytesIO(self.payload[name]))
                extracted = root / (case + '-extracted')
                with self.subTest(case=case), self.assertRaises(ValueError):
                    archive.extract_checked(path, self.payload, extracted)
                self.assertFalse(extracted.exists())

    def test_stale_hash_private_marker_and_extra_source_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            source = self.copy_source(folder)
            original = (source / 'README.md').read_bytes()
            (source / 'README.md').write_bytes(original + b'changed')
            with self.assertRaisesRegex(AssertionError, 'README.md'):
                check.check_payload(source)
            (source / 'README.md').write_bytes(original)
            manifest_path = source / 'MANIFEST.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['note'] = '/' + 'home/' + 'private-marker'
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AssertionError, 'Private marker'):
                check.check_payload(source)
            manifest_path.write_bytes(self.payload['MANIFEST.json'])
            (source / 'private-state.txt').write_text('not public')
            with self.assertRaises(AssertionError):
                check.check_payload(source)
            if sys.platform != 'win32':
                (source / 'private-state.txt').unlink()
                manifest_path.unlink()
                manifest_path.symlink_to(source.parent / 'unavailable-manifest')
                with self.assertRaisesRegex(AssertionError, 'Invalid manifest file'):
                    check.check_payload(source)


if __name__ == '__main__':
    unittest.main()
