#!/usr/bin/env python3
"""Local native primitives only: temporary state/own child, no service or GitHub."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import graph_platform as platform


def main():
    capabilities = platform.capabilities()
    assert capabilities['schema_version'] == 1
    assert capabilities['capabilities']['source_update']['available'] is False
    with tempfile.TemporaryDirectory(prefix='Community smoke spaces ') as temporary:
        state = Path(temporary) / 'private state'
        platform.private_directory(state)
        path = state / 'runtime.lock'
        child = None
        try:
            with platform.open_lock(path) as lock:
                platform.lock_exclusive(lock)
                with platform.coordinator_launch(lock.fileno()) as options:
                    child = subprocess.Popen([sys.executable, '-c', 'import sys;sys.stdin.buffer.read()'],
                                             stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL, **options)
                assert platform.process_start(child.pid)
            with platform.open_lock(path) as contender:
                try:
                    platform.lock_exclusive(contender)
                except BlockingIOError:
                    pass
                else:
                    raise RuntimeError('Inherited child did not retain runtime exclusion')
        finally:
            if child is not None:
                child.communicate(timeout=10)
        with platform.open_lock(path) as lock:
            platform.lock_exclusive(lock)
    print(json.dumps({'platform': capabilities['platform'], 'local_primitives': 'PASS',
                      'source_update': 'unavailable', 'native_hooks': 'unverified',
                      'scope': 'own temporary state/process only; no service/client/account qualification'}))


if __name__ == '__main__':
    main()
