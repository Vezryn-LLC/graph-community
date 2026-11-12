#!/usr/bin/env python3
"""Experimental per-user launchd CLI for the shared watcher. No forced stops."""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import contextmanager
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile
import tomllib

import graph_platform as platform

ROOT = Path(__file__).resolve().parent
CONFIG, STATE = (path.absolute() for path in platform.paths())
LABEL = 'org.graph.community'
PLIST = Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')
BIN = Path.home() / '.local/bin/graph'
PROFILES = ('GH_CONFIG_DIR', 'CODEX_HOME')
AUTH_OVERRIDES = ('GH_TOKEN', 'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN',
                  'GH_HOST', 'OPENAI_API_KEY', 'CODEX_API_KEY', 'CODEX_ACCESS_TOKEN',
                  'OPENAI_IDENTITY_TOKEN_FILE', 'OPENAI_FEDERATION_RULE_ID', 'CODEX_SQLITE_HOME')


def profiles():
    """Opt in with existing private absolute directories; never create/fix auth."""
    if any(key in os.environ for key in PROFILES) and not all(key in os.environ for key in PROFILES):
        raise RuntimeError('Isolated launch requires both GH_CONFIG_DIR and CODEX_HOME')
    values = {}
    for key in PROFILES:
        if key not in os.environ:
            continue
        raw = os.environ[key]
        path = Path(raw)
        if not path.is_absolute() or any(ord(char) < 32 or ord(char) == 127 for char in raw):
            raise RuntimeError(key + ' requires an absolute private directory')
        # Do not echo a malformed value: it may be a pasted credential.
        try:
            platform.check_private(path, directory=True)
        except (OSError, RuntimeError):
            raise RuntimeError(key + ' requires an existing private owned directory without links/ACLs') from None
        values[key] = str(path)
    return values


def isolated_environment():
    """Pin file auth for descendants without exposing tokens to launchd/argv/logs."""
    selected = profiles()
    env = dict(os.environ)
    if not selected:
        return env
    for key in AUTH_OVERRIDES:
        env.pop(key, None)
    try:
        if 'GH_CONFIG_DIR' in selected:
            path = Path(selected['GH_CONFIG_DIR']) / 'hosts.yml'
            platform.check_private(path)
            # This opt-in handoff uses JSON (valid YAML); no keyring-aware gh
            # command is safe here, including `gh config get oauth_token`.
            with platform.private_read(path, limit=65536) as file:
                token = json.load(file)['github.com']['oauth_token']
            if not isinstance(token, str) or not token or any(char.isspace() or ord(char) < 32 for char in token):
                raise ValueError('Invalid token')
            env['GH_TOKEN'] = token  # Environment only; stays pinned if file disappears.
            env['GH_HOST'] = 'github.com'
        if 'CODEX_HOME' in selected:
            path = Path(selected['CODEX_HOME']) / 'config.toml'
            platform.check_private(path)
            with platform.private_read(path, limit=65536) as file:
                config = tomllib.loads(file.read().decode())
            if config.get('cli_auth_credentials_store') != 'file':
                raise ValueError('File credential store required')
            if 'GH_CONFIG_DIR' in selected and config.get('shell_environment_policy') != {
                    'inherit': 'all', 'ignore_default_excludes': True}:
                raise ValueError('Pinned gh environment must reach native command descendants')
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        raise RuntimeError('Isolated file authentication unavailable; follow the Mac profile handoff') from None
    return env


def run_agent():
    installed()
    env = isolated_environment()
    os.execve(sys.executable, [sys.executable, '-B', '-u', str(ROOT / 'watcher.py'), 'watch'], env)


def target():
    return f'gui/{os.getuid()}/{LABEL}'


def launchctl(*args):
    return subprocess.run(['/bin/launchctl', *args], capture_output=True, text=True, timeout=10)


def checked(*args):
    result = launchctl(*args)
    if result.returncode:
        raise RuntimeError('launchctl failed; no forced retry: ' + result.stderr.strip()[:400])
    return result


def manifest():
    selected = profiles()
    command = [str(ROOT / 'graph_macos.py'), '_run-agent'] if selected else [str(ROOT / 'watcher.py'), 'watch']
    return {'Label': LABEL, 'ProgramArguments': [sys.executable, '-B', '-u', *command],
            'WorkingDirectory': str(ROOT), 'RunAtLoad': True, 'KeepAlive': False,
            'AbandonProcessGroup': True, 'ExitTimeOut': 0, 'Umask': 0o077,
            'StandardOutPath': str(STATE / 'runner.log'), 'StandardErrorPath': str(STATE / 'runner.log'),
            'EnvironmentVariables': {'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                                     'VEZRYN_GRAPH_ROOT': str(ROOT), 'VEZRYN_GRAPH_PYTHON': sys.executable,
                                     'VEZRYN_GRAPH_CONFIG': str(CONFIG),
                                     'VEZRYN_GRAPH_STATE': str(STATE),
                                     'VEZRYN_GRAPH_LIBRARY': str(Path(os.environ.get('VEZRYN_GRAPH_LIBRARY', str(CONFIG.parent / 'library'))).expanduser().absolute()),
                                     **selected}}


def installed():
    platform.check_private(PLIST)
    value = plistlib.loads(PLIST.read_bytes())
    expected = manifest()
    # PATH is captured at installation, not guessed from launchd's environment.
    env = value.get('EnvironmentVariables', {})
    if not isinstance(env.get('PATH'), str) or not env['PATH']:
        raise RuntimeError('Installed agent PATH unavailable; inspect installation')
    expected['EnvironmentVariables']['PATH'] = env['PATH']
    if value != expected:
        raise RuntimeError('Installed agent belongs to different source/configuration; refusing replacement/control')
    return value


def owned_bin():
    if BIN.exists() or BIN.is_symlink():
        if not BIN.is_symlink() or BIN.resolve() != ROOT / 'graph_macos.py' or BIN.lstat().st_uid != os.getuid():
            raise RuntimeError(f'Refusing unrelated CLI at {BIN}')


def container(path):
    # LaunchAgents and .local/bin may contain unrelated user files; never chmod.
    path.mkdir(parents=True, exist_ok=True)
    platform.check_private(path, directory=True, shared=True)

def write_private(path, data):
    if path.exists() or path.is_symlink():
        platform.check_private(path)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(data)
        platform.check_private(temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def control():
    platform.prepare_state(STATE)
    with platform.open_lock(STATE / 'update.lock') as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError as error:
            raise RuntimeError('Graph control is already in progress') from error
        yield


def runtime_busy():
    path = STATE / 'watcher.lock'
    if not path.exists() and not path.is_symlink():
        return False
    with platform.open_lock(path) as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError:
            return True
    return False


def recovery_hold():
    import watcher
    return watcher.local_ownership_hold()


def launchd_job(raw):
    """Read immediate job entries; nested coalition/LWCR fields are not job fields."""
    lines = raw.splitlines()
    if not lines or lines[0].strip() != target() + ' = {':
        raise RuntimeError('Malformed launchd job; ownership unknown')
    fields, blocks = {}, {}
    depth, current = 1, None
    for line in lines[1:]:
        text = line.strip()
        if not text:
            if depth == 2 and current in ('arguments', 'environment'):
                blocks[current].append('')
            continue
        if depth == 0:
            raise RuntimeError('Malformed launchd job; ownership unknown')
        if text == '}':
            depth -= 1
            if depth == 1:
                current = None
            continue
        # launchctl uses both assignments and dictionary arrows in nested LWCR
        # output. Top-level fields still require the ordinary assignment syntax.
        opens_block = text.endswith(' = {') or (depth > 1 and text.endswith(' => {'))
        if depth == 1:
            match = re.fullmatch(r'([^=]+) = (.+)', text)
            if not match:
                raise RuntimeError('Malformed launchd field; ownership unknown')
            key, content = match.groups()
            if key in fields or key in blocks:
                raise RuntimeError('Ambiguous launchd status; ownership unknown')
            if content == '{':
                current = key
                blocks[key] = []
            else:
                fields[key] = content
        elif current in ('arguments', 'environment'):
            # These blocks must be flat; do not hide values in nested scopes.
            if depth != 2 or opens_block:
                raise RuntimeError('Malformed launchd configuration; ownership unknown')
            blocks[current].append(line.lstrip())
        if opens_block:
            depth += 1
    if depth != 0:
        raise RuntimeError('Incomplete launchd job; ownership unknown')
    return fields, blocks


def agent(value):
    result = launchctl('print', target())
    if result.returncode:
        # Other errors (bus, permission, changed output) cannot establish absence.
        if result.returncode == 113 and 'Could not find service' in result.stderr:
            return {'registered': False, 'pid': 0}
        raise RuntimeError('launchd status unavailable; ownership unknown: ' + result.stderr.strip()[:300])
    raw = result.stdout
    if len(raw) > 65536:
        raise RuntimeError('launchd status incomplete; ownership unknown')
    fields, blocks = launchd_job(raw)
    scalar_keys = ('path', 'program', 'pid', 'state', 'working directory')
    if any(key in blocks for key in scalar_keys) or any(key in fields for key in ('arguments', 'environment')):
        raise RuntimeError('Malformed launchd field type; ownership unknown')
    fields = {key: fields.get(key) for key in scalar_keys}
    argv = [line.strip() for line in blocks['arguments']] if 'arguments' in blocks else None
    if fields['path'] != str(PLIST) or fields['program'] != value['ProgramArguments'][0] or argv != value['ProgramArguments'] or fields['working directory'] != value['WorkingDirectory']:
        raise RuntimeError('Loaded launchd source/argv unverified; refusing control')
    environment = {}
    for line in blocks.get('environment', []):
        match = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*) => (.*)', line)
        if not match or match[1] in environment:
            raise RuntimeError('Loaded launchd environment ambiguous; ownership unknown')
        environment[match[1]] = match[2]
    if any(environment.get(key) != expected for key, expected in value['EnvironmentVariables'].items()):
        raise RuntimeError('Loaded launchd configuration/environment unverified; refusing control')
    if any(environment.get(key) != value['EnvironmentVariables'].get(key) for key in PROFILES):
        raise RuntimeError('Loaded launchd profiles unverified; refusing control')
    if any(key in value['EnvironmentVariables'] for key in PROFILES) and any(key in environment for key in AUTH_OVERRIDES):
        raise RuntimeError('Loaded launchd authentication override; refusing control')
    if fields['pid'] is not None:
        if fields['state'] != 'running' or not fields['pid'].isascii() or not fields['pid'].isdecimal() or int(fields['pid']) < 1:
            raise RuntimeError('launchd PID unavailable; ownership unknown')
        return {'registered': True, 'pid': int(fields['pid'])}
    if fields['state'] != 'not running':
        raise RuntimeError('launchd process state unknown; refusing control')
    return {'registered': True, 'pid': 0}


def status():
    value = {'schema_version': 1, 'service': 'unknown', 'eligible': False, **platform.capabilities()}
    try:
        platform.prepare_state(STATE)
        info = agent(installed())
        value.update(info)
        busy = runtime_busy()
        if not info['pid']:
            hold = recovery_hold()
            value['service'] = 'draining' if busy else 'unknown' if hold else 'stopped'
            if hold:
                value['diagnostic'] = hold
            return value
        from graph_update import read_json, runtime_hash
        receipt = read_json(STATE / 'watcher-launch.json')
        start = platform.process_start(info['pid'])
        if receipt.get('pid') != info['pid'] or receipt.get('start') != start or receipt.get('root') != str(ROOT) or not busy:
            raise RuntimeError('Watcher PID/lifetime/source/lock unverified; ownership unknown')
        value.update(service='draining' if (STATE / 'stop-request').exists() else 'running',
                     running=receipt.get('revision'), runtimeMatches=receipt.get('runtime') == runtime_hash())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        value['diagnostic'] = str(error)
    return value


def runner_prerequisites():
    platform.launch_prerequisites()
    if not Path('/bin/launchctl').is_file():
        raise RuntimeError('Native launchctl unavailable')


def install():
    if sys.version_info < (3, 11):
        raise RuntimeError('Python 3.11+ required')
    runner_prerequisites()
    manifest()  # Reject unsafe opt-ins before creating installation/state files.
    owned_bin()
    if PLIST.exists() or PLIST.is_symlink():
        installed()  # Exact matching installs are idempotent, never rewritten.
    with control():
        owned_bin()
        if PLIST.exists() or PLIST.is_symlink():
            installed()
        container(PLIST.parent)
        container(BIN.parent)
        platform.private_directory(ROOT / '.graph')
        if not PLIST.exists():
            write_private(PLIST, plistlib.dumps(manifest()))
        log = STATE / 'runner.log'
        if not log.exists():
            write_private(log, b'')
        if not BIN.is_symlink():
            BIN.symlink_to(ROOT / 'graph_macos.py')
    return 'Installed experimental user LaunchAgent and CLI; no load/start operation performed'


def start():
    with control():
        value = installed()
        isolated_environment()  # Validate now and again on every launch/login.
        runner_prerequisites()
        info = agent(value)
        if info['pid'] or runtime_busy():
            observed = status()
            if observed['service'] not in ('running', 'draining') or not info['pid']:
                raise RuntimeError('Existing runtime ownership unknown; preserving processes and stop request')
            (STATE / 'stop-request').unlink(missing_ok=True)
            return 'Graph is already running; stop request canceled if present'
        # Shared watcher reconciles durable pending/journal state before dispatch.
        # Never kickstart -k, kill, restart or reset that state.
        (STATE / 'stop-request').unlink(missing_ok=True)
        if info['registered']:
            checked('kickstart', target())
        else:
            checked('bootstrap', f'gui/{os.getuid()}', str(PLIST))
    return 'Graph start requested; use status to verify the native watcher'


def stop():
    with control():
        installed()
        write_private(STATE / 'stop-request', b'')
    return 'Graph stopping: no new assignments; active native coordination finishes before exit'


def uninstall():
    with control():
        value = installed()
        owned_bin()
        # Hold the same lock as the watcher throughout removal. bootout is only
        # allowed for a known idle job, never used to stop active coordination.
        with platform.open_lock(STATE / 'watcher.lock') as lock:
            try:
                platform.lock_exclusive(lock)
            except BlockingIOError as error:
                raise RuntimeError('Runtime still owned; request stop and wait before uninstalling') from error
            hold = recovery_hold()
            if hold:
                raise RuntimeError('Worker/effect ownership unresolved; preserve installation: ' + hold)
            info = agent(value)
            if info['pid']:
                raise RuntimeError('Watcher process remains; stop and verify exit before uninstalling')
            if info['registered']:
                checked('bootout', target())
            PLIST.unlink()
            if BIN.is_symlink():
                BIN.unlink()
    return 'Removed owned LaunchAgent and CLI; config, logs, recovery state and source preserved'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('install', 'start', 'stop', 'logs', 'uninstall', 'capabilities', 'version', 'check-update', 'apply-update', 'doctor', 'queue', 'library', '_run-agent'):
        command_parser = sub.add_parser(name)
        if name in ('version', 'check-update', 'apply-update', 'doctor', 'queue'):
            command_parser.add_argument('--json', action='store_true')
        if name == 'library':
            command_parser.add_argument('--explain', action='store_true')
    sub.add_parser('status').add_argument('--json', action='store_true')
    repo = sub.add_parser('repo')
    repo.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.command == 'capabilities':
            print(json.dumps(platform.capabilities()))
            return 0
        if platform.platform_name() != 'macos':
            raise RuntimeError('This experimental runner requires macOS; use bin/graph on Linux')
        if args.command in ('version', 'check-update', 'apply-update', 'repo', 'doctor', 'queue', 'library'):
            file = 'graph_update.py' if args.command in ('version', 'check-update', 'apply-update') else 'watcher.py'
            extra = args.args if args.command == 'repo' else ['--explain'] if getattr(args, 'explain', False) else ['--json'] if getattr(args, 'json', False) else []
            return subprocess.call([sys.executable, '-B', str(ROOT / file), args.command, *extra])
        if args.command == 'status':
            value = status()
            print(json.dumps(value) if args.json else 'Graph: ' + value['service'] + (' · ' + value['diagnostic'] if value.get('diagnostic') else ''))
        elif args.command == 'logs':
            platform.check_private(STATE / 'runner.log')
            with (STATE / 'runner.log').open() as log:
                print(''.join(deque(log, maxlen=40)), end='')
        elif args.command == '_run-agent':
            run_agent()
        else:
            print(globals()[args.command]())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
