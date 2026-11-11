"""Fixed local Graph revision checks and explicit, drain-first activation.

No caller-selected repository, executable, shell command or service is accepted.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import graph_platform as platform

ROOT = Path(__file__).resolve().parent
_, STATE = platform.paths()
RUNTIME = ('watcher.py', 'library.py', 'graph_update.py', 'graph_platform.py')


def run(*args, timeout=5):
    try:
        result = subprocess.run((platform.executable(args[0]), *args[1:]), cwd=ROOT, text=True, capture_output=True,
                                timeout=timeout, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0', 'GH_PROMPT_DISABLED': '1'})
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f'{args[0]} unavailable or timed out; refresh before retrying') from error
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr.strip()[:400] or "command unsuccessful"}')
    return result.stdout.strip()


def git(*args):
    return run('git', '-c', 'core.fsmonitor=false', *args)


def read_json(path):
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def write_json(path, value):
    platform.require("private_state")
    platform.prepare_state(STATE)
    tmp = path.with_suffix(f'.{os.getpid()}.tmp')
    platform.file_target(path)
    platform.file_target(tmp)
    with tmp.open('w') as output:
        platform.file_permissions(tmp)
        json.dump(value, output)
        output.flush()
        os.fsync(output.fileno())
    tmp.replace(path)
    if platform.platform_name() == 'linux':
        fd = os.open(STATE, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def runtime_hash():
    digest = hashlib.sha256()
    names = (*RUNTIME, 'graph_windows_native.py') if platform.platform_name() == 'windows' else RUNTIME
    for name in names:
        digest.update(name.encode())
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()


def process_start(pid):
    return platform.process_start(pid)


def record_launch():
    """Local lifetime/runtime evidence; unknown Git revision never grants activation."""
    try:
        try:
            revision = git('rev-parse', 'HEAD')
            dirty = bool(git('status', '--porcelain'))
        except RuntimeError:
            revision, dirty = None, True
        write_json(STATE / 'watcher-launch.json', {
            'runner': os.environ.get('VEZRYN_GRAPH_RUNNER_ID'),
            'config': str(platform.paths()[0].absolute()), 'state': str(STATE.absolute()),
            'pid': os.getpid(), 'start': process_start(os.getpid()), 'root': str(ROOT),
            'revision': revision, 'dirty': dirty, 'runtime': runtime_hash(),
            'launchedAt': int(time.time())})
    except (RuntimeError, OSError):
        pass  # Unknown native evidence remains unknown; graceful stop is preserved.


def snapshot(check_remote=False):
    return {**platform.capabilities(), 'summary': 'No reviewed Community update origin',
            'eligible': False, 'service': 'unknown',
            'diagnostic': 'Source activation unavailable; drain/reconcile before installing a reviewed snapshot'}


def activate():
    raise RuntimeError('No reviewed Community update origin; source activation unavailable')


def main():
    args = sys.argv[1:]
    if (not args or args[0] not in ('version', 'check-update', 'apply-update')
            or args[1:] not in ([], ['--json'])):
        print('Usage: graph {version|check-update|apply-update} [--json]', file=sys.stderr)
        return 2
    try:
        value = activate() if args[0] == 'apply-update' else snapshot()
        print(json.dumps(value))
        return 0
    except (RuntimeError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
