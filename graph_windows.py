#!/usr/bin/env python3
"""Experimental native Windows per-user CLI; manual detached start, no task kills."""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import contextmanager
import hashlib
import json
import ntpath
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import graph_platform as platform
from graph_windows_native import api

ROOT = Path(__file__).resolve().parent
CONFIG, STATE = (path.absolute() for path in platform.paths())
INSTALL = CONFIG.parent / 'windows-runner'
MANIFEST = INSTALL / 'installation.json'
ENTRY = INSTALL / 'graph.py'
START = STATE / 'windows-start.json'


def manifest():
    return {'schema_version': 1, 'root': str(ROOT), 'python': sys.executable,
            'config': str(CONFIG), 'state': str(STATE), 'startup': 'manual-detached',
            'environment': {'PATH': os.environ.get('PATH', ''),
                            'VEZRYN_GRAPH_ROOT': str(ROOT), 'VEZRYN_GRAPH_PYTHON': sys.executable,
                            'VEZRYN_GRAPH_CONFIG': str(CONFIG), 'VEZRYN_GRAPH_STATE': str(STATE),
                            'VEZRYN_GRAPH_LIBRARY': str(Path(os.environ.get('VEZRYN_GRAPH_LIBRARY', str(CONFIG.parent / 'library'))).expanduser().absolute())}}


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def launcher():
    return ('import os,sys\n' + f'os.execv({sys.executable!r}, [{sys.executable!r}, "-B", {str(ROOT / "graph_windows.py")!r}, *sys.argv[1:]])\n').encode()


def write(path, value):
    platform.private_directory(path.parent)
    platform.file_target(path)
    if path.exists() or path.is_symlink():
        platform.check_private(path)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            platform.file_permissions(temporary)
            stream.write(value if isinstance(value, bytes) else (json.dumps(value, sort_keys=True) + '\n').encode())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def read(path):
    with platform.private_read(path, 65536) as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError('Invalid private Windows runner evidence')
    return value


def installed():
    value, expected = read(MANIFEST), manifest()
    environment = value.get('environment', {})
    if not isinstance(environment, dict) or not isinstance(environment.get('PATH'), str):
        raise RuntimeError('Installed native environment unknown')
    expected['environment']['PATH'] = environment['PATH']
    if value != expected:
        raise RuntimeError('Different Windows source/configuration installed; refusing control/replacement')
    with platform.private_read(ENTRY, 65536) as stream:
        if stream.read() != launcher():
            raise RuntimeError('Unrelated Windows CLI entry; refusing replacement')
    return value


@contextmanager
def control():
    platform.prepare_state(STATE)
    with platform.open_lock(STATE / 'update.lock') as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError as error:
            raise RuntimeError('Windows Graph control is already owned') from error
        yield


def runtime_busy():
    with platform.open_lock(STATE / 'watcher.lock') as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError:
            return True
    return False


def status():
    value = {**platform.capabilities(), 'service': 'unknown', 'eligible': False, 'startup_integration': False}
    try:
        platform.prepare_state(STATE)
        source = installed()
        busy = runtime_busy()
        platform.file_target(START)
        requested = read(START) if START.exists() else None
        if requested is not None and (requested.get('phase') != 'spawned' or requested.get('installation') != identity(source)):
            raise RuntimeError('Prior startup outcome/source unknown; reconcile the preserved start intent before retrying')
        process = None
        if requested is not None:
            if type(requested.get('pid')) is not int or requested['pid'] < 1 or not isinstance(requested.get('start'), str):
                raise RuntimeError('Native launch process identity missing; no duplicate start')
            process = api().process(requested['pid'])
            if process and (process['start'] != requested['start'] or ntpath.normcase(process['image']) != ntpath.normcase(source['python'])):
                raise RuntimeError('PID reused or native process/source identity mismatched; ownership unknown')
        if process:
            receipt = read(STATE / 'watcher-launch.json')
            expected = {'pid': requested['pid'], 'start': process['start'], 'root': source['root'],
                        'runner': identity(source), 'config': source['config'], 'state': source['state']}
            if not busy or any(receipt.get(key) != expected[key] for key in expected):
                raise RuntimeError('Native watcher launch/source/lock evidence incomplete; refresh without relaunch')
            from graph_update import runtime_hash
            value.update(service='draining' if (STATE / 'stop-request').exists() else 'running',
                         pid=requested['pid'], start=process['start'], running=receipt.get('revision'),
                         runtimeMatches=receipt.get('runtime') == runtime_hash())
            return value
        import watcher
        hold = watcher.local_ownership_hold()
        value['service'] = 'draining' if busy else 'unknown' if hold else 'stopped'
        if hold:
            value['diagnostic'] = hold
    except (OSError, ValueError, RuntimeError) as error:
        value['diagnostic'] = str(error)
    return value


def install():
    if sys.version_info < (3, 11):
        raise RuntimeError('Native Python 3.11+ required')
    platform.launch_prerequisites()
    with control():
        journal = platform.native_journal(ROOT, STATE)
        platform.private_directory(INSTALL)
        if MANIFEST.exists() or ENTRY.exists() or MANIFEST.is_symlink() or ENTRY.is_symlink():
            installed()  # Matching reinstall is preserved; partial/foreign install fails closed.
        else:
            write(ENTRY, launcher())
            write(MANIFEST, manifest())
        platform.private_directory(journal.parent)
        if not (STATE / 'runner.log').exists():
            write(STATE / 'runner.log', b'')
    return f'Installed experimental native CLI: {ENTRY}. No startup/task/PATH settings changed.'


def start():
    with control():
        source = installed()
        platform.launch_prerequisites()
        observed = status()
        if observed['service'] in ('running', 'draining') and observed.get('pid'):
            (STATE / 'stop-request').unlink(missing_ok=True)
            return 'Graph already running; stop request canceled if present'
        if observed['service'] != 'stopped':
            raise RuntimeError('Native ownership/startup unresolved; preserving processes and stop request: ' + observed.get('diagnostic', observed['service']))
        (STATE / 'stop-request').unlink(missing_ok=True)
        # Durable before process creation. A CLI crash/failed launch cannot make
        # another invocation infer that no watcher was launched.
        write(START, {'phase': 'starting', 'installation': identity(source)})
        log = STATE / 'runner.log'
        platform.check_private(log)
        environment = {**os.environ, **source['environment'], 'VEZRYN_GRAPH_RUNNER_ID': identity(source)}
        with log.open('ab') as output:
            proc = subprocess.Popen([source['python'], '-B', '-u', str(ROOT / 'watcher.py'), 'watch'],
                                    cwd=ROOT, env=environment, stdin=subprocess.DEVNULL, stdout=output,
                                    stderr=subprocess.STDOUT, close_fds=True, creationflags=0x208)
        process = api().process(proc.pid)
        if not process:
            raise RuntimeError('Watcher exited during startup; preserve intent/log and reconcile before retrying')
        write(START, {'phase': 'spawned', 'installation': identity(source), 'pid': proc.pid, 'start': process['start']})
    return 'Native Graph start requested; status must verify its launch receipt'


def stop():
    with control():
        installed()
        write(STATE / 'stop-request', b'')
    return 'Graph stopping: no new assignments; active native coordination drains without termination'


def uninstall():
    with control():
        installed()
        observed = status()
        if observed['service'] != 'stopped':
            raise RuntimeError('Stop and reconcile native ownership before uninstall: ' + observed.get('diagnostic', observed['service']))
        with platform.open_lock(STATE / 'watcher.lock') as lock:
            try:
                platform.lock_exclusive(lock)
            except BlockingIOError as error:
                raise RuntimeError('Runtime still owned; no source removed') from error
            installed()
            ENTRY.unlink()
            MANIFEST.unlink()
    return 'Removed owned CLI/installation manifest; all source, config, logs and recovery evidence preserved'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('install', 'start', 'stop', 'uninstall', 'logs', 'capabilities', 'version', 'check-update', 'apply-update', 'library'):
        command_parser = sub.add_parser(command)
        if command in ('version', 'check-update', 'apply-update'):
            command_parser.add_argument('--json', action='store_true')
    sub.add_parser('status').add_argument('--json', action='store_true')
    sub.add_parser('repo').add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.command == 'capabilities':
            print(json.dumps({**platform.capabilities(), 'startup_integration': False}))
            return 0
        if platform.platform_name() != 'windows':
            raise RuntimeError('Native Windows runner requires Windows; Linux/WSL is not a substitute')
        if args.command in ('repo', 'library', 'version', 'check-update', 'apply-update'):
            file = 'watcher.py' if args.command in ('repo', 'library') else 'graph_update.py'
            return subprocess.call([sys.executable, '-B', str(ROOT / file), args.command, *(args.args if args.command == 'repo' else ['--json'] if getattr(args, 'json', False) else [])])
        if args.command == 'status':
            value = status()
            print(json.dumps(value) if args.json else 'Graph: ' + value['service'] + (' · ' + value['diagnostic'] if value.get('diagnostic') else ''))
        elif args.command == 'logs':
            with platform.private_read(STATE / 'runner.log', 1024 * 1024 * 1024) as log:
                print(b''.join(deque(log, maxlen=40)).decode('utf-8', errors='replace'), end='')
        else:
            print(globals()[args.command]())
    except (OSError, ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
