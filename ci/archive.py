"""Build and check one deterministic, reviewed source-only tar archive."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

import check


def modes(payload):
    manifest = json.loads(payload['MANIFEST.json'])
    return {name: int(record['mode'], 8) for name, record in manifest['files'].items()} | {'MANIFEST.json': 0o644}


def write_archive(destination, payload):
    """Exclusive creation: an existing artifact is never replaced."""
    permissions = modes(payload)
    output = destination.open('xb')
    try:
        with output:
            with tarfile.open(fileobj=output, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for name in sorted(payload):
                    member = tarfile.TarInfo(name)
                    member.size = len(payload[name])
                    member.mode = permissions[name]
                    member.mtime = member.uid = member.gid = 0
                    member.uname = member.gname = ''
                    archive.addfile(member, io.BytesIO(payload[name]))
    except BaseException:
        destination.unlink()
        raise


def extract_checked(archive_path, payload, destination):
    """Compare to the validated source snapshot before writing any member."""
    permissions = modes(payload)
    with tarfile.open(archive_path, mode='r:') as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if names != sorted(payload):
            raise ValueError('archive file list differs from the reviewed payload')
        for member in members:
            if (not member.isfile() or member.mode != permissions[member.name]
                    or member.mtime != 0 or member.uid != 0 or member.gid != 0
                    or member.uname or member.gname
                    or member.size != len(payload[member.name])):
                raise ValueError('archive metadata differs from the canonical payload')
            with archive.extractfile(member) as stream:
                if stream.read() != payload[member.name]:
                    raise ValueError('archive bytes differ from the validated source')
        # Names are the fixed positive allowlist, with no links or directory entries.
        destination.mkdir()
        for name in sorted(payload):
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as output:
                output.write(payload[name])
            path.chmod(permissions[name])


def build(source, destination):
    if destination.resolve().is_relative_to(source.resolve()):
        raise ValueError('put the archive outside the source checkout')
    payload = check.check_payload(source)
    history = check.check_history(source)
    created = False
    try:
        write_archive(destination, payload)
        created = True
        with tempfile.TemporaryDirectory(prefix='Community archive ') as temporary:
            extracted = Path(temporary) / 'source'
            extract_checked(destination, payload, extracted)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            subprocess.run([sys.executable, '-B', 'ci/check.py'], cwd=extracted,
                           env=env, check=True, timeout=120)
        return {'archive': destination.name, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'files': len(payload), 'manifest_sha256': hashlib.sha256(payload['MANIFEST.json']).hexdigest(),
                'extracted_check': 'PASS', 'source_history': history,
                'release_or_native_host_qualification': 'not performed'}
    except BaseException:
        if created:
            destination.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='new .tar path outside this source checkout')
    args = parser.parse_args()
    try:
        print(json.dumps(build(check.ROOT, args.archive)))
    except (AssertionError, OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Archive check failed: {error}\n')


if __name__ == '__main__':
    main()
