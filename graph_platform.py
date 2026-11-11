"""Thin OS boundary. Capability availability is not installation qualification."""
from __future__ import annotations

from contextlib import contextmanager

import errno
import json
import os
from pathlib import Path
import shutil
import stat
import sys


def platform_name():
    if sys.platform.startswith('linux'):
        return 'linux'
    return {'darwin': 'macos', 'win32': 'windows'}.get(sys.platform, 'unknown')


def paths():
    """Resolve paths without creating them; explicit legacy overrides win."""
    home = Path.home()
    name = platform_name()
    if name == 'macos':
        config = home / 'Library/Application Support/graph-community/repos.toml'
        state = home / 'Library/Application Support/graph-community/state'
    elif name == 'windows':
        base = Path(os.environ.get('LOCALAPPDATA', str(home / 'AppData/Local'))) / 'graph-community'
        config, state = base / 'repos.toml', base / 'state'
    else:
        config = home / '.config/graph-community/repos.toml'
        state = home / '.local/state/graph-community'
    return (Path(os.environ.get('VEZRYN_GRAPH_CONFIG', str(config))).expanduser(),
            Path(os.environ.get('VEZRYN_GRAPH_STATE', str(state))).expanduser())


def native_journal(root, state=None):
    """Windows sandbox workspaces are writable; ownership facts stay private."""
    legacy = root / '.graph/subagent-events.jsonl'
    if platform_name() != 'windows':
        return legacy
    try:
        legacy.lstat()
    except FileNotFoundError:
        pass
    else:
        raise RuntimeError('Legacy Windows native journal requires ownership reconciliation; preserve history')
    return (paths()[1] if state is None else state) / 'subagent-events.jsonl'


def capabilities():
    """v1 reports implemented adapters, never live service/worker ownership.

    Consumers must reject unknown schema versions and require availability plus
    operation-specific evidence. No native hook availability is inferred here.
    """
    name = platform_name()
    linux = name == 'linux'
    implemented_os = name in ('linux', 'macos', 'windows')
    implemented = ('private_state', 'runtime_lock', 'inherited_lock', 'process_identity',
                   'coordinator_launch', 'service_control', 'source_update')
    values = {key: {'available': implemented_os if key != 'source_update' else linux,
                    'diagnostic': ('Experimental OS adapter; real host qualification pending' if name in ('macos', 'windows') and key != 'source_update'
                                   else '' if linux else 'OS adapter unqualified; runtime ownership/control unavailable')}
              for key in implemented}
    values['source_update'] = {'available': False, 'diagnostic': 'No reviewed Community update origin; source activation unavailable'}
    values['native_hooks'] = {'available': False, 'diagnostic': 'Trusted native lifecycle delivery must be verified separately'}
    return {'schema_version': 1, 'platform': platform_name(),
            'capabilities': values,
            'prerequisites': {item: prerequisite(item) for item in ('git', 'gh', 'codex', 'systemctl', 'launchctl')},
            'receipt_schema_version': 1, 'journal_format': 'legacy-jsonl',
            'qualification': 'experimental-unverified' if name in ('macos', 'windows') else 'existing-linux' if linux else 'unavailable'}


def require(capability):
    value = capabilities()['capabilities'][capability]
    if not value['available']:
        raise RuntimeError(f'{capability} unavailable on {platform_name()}: {value["diagnostic"]}')


def lock_exclusive(file, *, blocking=False):
    require('runtime_lock')
    # Import only after capability validation: Windows must still import/read JSON.
    if platform_name() == 'windows':
        if blocking:
            raise RuntimeError('Blocking intent lock is only used by the Linux source controller')
        file.acquire()
        return
    import fcntl
    fcntl.flock(file, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))


def coordinator_options(lock_fd):
    require('inherited_lock')
    if platform_name() == 'windows':
        raise RuntimeError('Use the Windows coordinator launch context for bounded handle inheritance')
    return {'pass_fds': () if lock_fd is None else (lock_fd,)}


@contextmanager
def coordinator_launch(lock_fd):
    if platform_name() != 'windows':
        yield coordinator_options(lock_fd)
        return
    if lock_fd is None:
        raise RuntimeError('Native Windows coordinator requires an owned runtime handle')
    import subprocess
    from graph_windows_native import api
    duplicate = api().duplicate(lock_fd)
    try:
        startup = subprocess.STARTUPINFO(lpAttributeList={'handle_list': [duplicate]})
        yield {'startupinfo': startup, 'close_fds': True}
    finally:
        api().k.CloseHandle(duplicate)


def executable(name):
    if platform_name() != 'windows':
        return native_codex() if name == 'codex' else name
    # Search explicit absolute PATH entries only: Windows current-directory
    # executable lookup must not turn task source into a native CLI prerequisite.
    for directory in os.environ.get('PATH', '').split(os.pathsep):
        base = Path(directory)
        if directory and base.is_absolute():
            candidate = base / (name + '.exe')
            if candidate.is_file():
                return str(candidate.resolve())
    raise FileNotFoundError(f'Native {name}.exe required on absolute PATH; batch shims/current-directory lookup unqualified')



def native_codex():
    """Bypass npm's Node shim: execve/spawn there can discard inherited locks.

    Resolve only the selected PATH installation, never an unrelated cached client.
    Unknown script launchers fail closed; install a native Codex binary on PATH.
    """
    selected = shutil.which('codex')
    if not selected:
        raise FileNotFoundError('Native Codex executable required on PATH')
    selected = Path(selected).resolve(strict=True)
    candidates = [selected]
    if selected.name == 'codex.js' and selected.parent.name == 'bin':
        root = selected.parent.parent
        try:
            package = json.loads((root / 'package.json').read_text())
        except (OSError, ValueError):
            package = {}
        if package.get('name') == '@openai/codex':
            machine = {'x86_64': 'x64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(os.uname().machine)
            target = {('linux', 'x64'): 'x86_64-unknown-linux-musl',
                      ('linux', 'arm64'): 'aarch64-unknown-linux-musl',
                      ('macos', 'x64'): 'x86_64-apple-darwin',
                      ('macos', 'arm64'): 'aarch64-apple-darwin'}.get((platform_name(), machine))
            if target:
                dependency = '@openai/codex-' + ('linux' if platform_name() == 'linux' else 'darwin') + '-' + machine
                # npm nested/hoisted optional dependency, then the legacy vendor layout.
                candidates = [root / 'node_modules' / dependency / 'vendor' / target / 'bin/codex',
                              root.parent.parent / dependency / 'vendor' / target / 'bin/codex',
                              root / 'vendor' / target / 'bin/codex']
    magic = (b'\x7fELF',) if platform_name() == 'linux' else (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe',
             b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca',
             b'\xca\xfe\xba\xbf', b'\xbf\xba\xfe\xca')
    for candidate in candidates:
        try:
            candidate = candidate.resolve(strict=True)
            if not candidate.is_file() or not os.access(candidate, os.X_OK):
                continue
            with candidate.open('rb') as binary:
                if binary.read(4) not in magic:
                    continue
            return str(candidate)
        except OSError:
            continue
    raise FileNotFoundError('Codex launcher cannot guarantee inherited locks; put the native Codex executable on PATH')


def prerequisite(name):
    if platform_name() == 'windows' and name in ('git', 'gh', 'codex'):
        try:
            executable(name)
            return True
        except FileNotFoundError:
            return False
    return bool(shutil.which(name))


def launch_prerequisites():
    require('coordinator_launch')
    missing = []
    for name in ('git', 'gh', 'codex'):
        try:
            if platform_name() == 'windows':
                executable(name)
            elif not shutil.which(name):
                missing.append(name)
        except FileNotFoundError:
            missing.append(name)

    if missing:
        raise FileNotFoundError('Coordinator prerequisites missing from PATH: ' + ', '.join(missing))


def process_start(pid):
    require('process_identity')
    if platform_name() == 'windows':
        from graph_windows_native import api
        value = api().process(pid)
        if value is None:
            raise ProcessLookupError('Native Windows process exited')
        return value['start']
    if platform_name() == 'macos':
        return macos_process_start(pid)
    # Linux stat field 22; command names may contain spaces or parentheses.
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]


def process_command(pid):
    require('process_identity')
    if platform_name() != 'linux':
        raise RuntimeError('Native argv evidence unavailable; source update remains unavailable')
    return Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]


def service_properties(run, unit):
    if platform_name() != 'linux':
        raise RuntimeError('Linux service properties unavailable; use the matching platform runner')
    require('service_control')
    raw = run('systemctl', '--user', 'show', unit, '--property=WorkingDirectory',
              '--property=ExecStart', '--property=MainPID', '--property=ActiveState', '--property=SubState',
              '--property=TasksCurrent', '--property=ControlGroup')
    return dict(line.split('=', 1) for line in raw.splitlines() if '=' in line)


def macos_process_start(pid):
    """Native microsecond birth time, not a PID/ps-time liveness guess.

    ABI: Apple's sys/proc_info.h, proc_bsdinfo / PROC_PIDTBSDINFO (3).
    Short/denied reads or another user's process are unknown, never matched.
    """
    import ctypes as c
    class BsdInfo(c.Structure):
        _fields_ = [('ids', c.c_uint32 * 12), ('comm', c.c_char * 16),
                    ('name', c.c_char * 32), ('counts', c.c_uint32 * 5),
                    ('nice', c.c_int32), ('seconds', c.c_uint64), ('micros', c.c_uint64)]
    info = BsdInfo()
    try:
        library = c.CDLL('/usr/lib/libproc.dylib', use_errno=True)
        call = library.proc_pidinfo
    except (OSError, AttributeError) as error:
        raise OSError('Native process lifetime API unavailable') from error
    call.argtypes = [c.c_int, c.c_int, c.c_uint64, c.c_void_p, c.c_int]
    call.restype = c.c_int
    count = call(pid, 3, 0, c.byref(info), c.sizeof(info))
    if count != c.sizeof(info) or info.ids[3] != pid or info.ids[5] != os.getuid() or not info.seconds:
        raise OSError('Native process lifetime identity unavailable')
    return f'{info.seconds}.{info.micros:06d}'


def check_private(path, directory=False, shared=False):
    """Mac state is owner-only, regular, unlinked and free of extended ACLs.

    Native ACL reads distinguish absent ACL metadata from permission/API failure.
    chmod and ls display markers are never treated as ACL removal/evidence.
    """
    if platform_name() == 'windows':
        from graph_windows_native import api
        api().check(path, directory, shared)
        return
    if platform_name() != 'macos':
        return
    info = path.lstat()
    valid = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    if not valid or info.st_uid != os.getuid() or info.st_mode & (0o022 if shared else 0o077):
        raise RuntimeError(f'Private owned {"directory" if directory else "file"} required: {path}')
    check_macos_acl(path)


def check_macos_acl(path):
    # Apple Libc acl_file.c/filesec.c: absent FILESEC_ACL sets ENOENT.
    # Recheck the existing inode so a missing/replaced path cannot mean no ACL.
    import ctypes as c
    before = path.lstat()
    try:
        library = c.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
        read = library.acl_get_link_np
        read.argtypes, read.restype = [c.c_char_p, c.c_int], c.c_void_p
        free = library.acl_free
        free.argtypes, free.restype = [c.c_void_p], c.c_int
    except (OSError, AttributeError) as error:
        raise RuntimeError(f'Native ACL inspection unavailable: {path}') from error
    c.set_errno(0)
    acl = read(os.fsencode(path), 0x100)  # ACL_TYPE_EXTENDED
    error = c.get_errno()
    if acl:
        free(acl)
        raise RuntimeError(f'Extended ACL present; private permissions unverified: {path}')
    after = path.lstat()
    identity = lambda info: (info.st_dev, info.st_ino, info.st_uid, info.st_mode,
                             info.st_nlink, info.st_ctime_ns)
    if error != errno.ENOENT or identity(before) != identity(after):
        raise RuntimeError(f'Native ACL read failed; private permissions unverified: {path}')


def private_directory(path):
    require('private_state')
    if platform_name() == 'windows':
        from graph_windows_native import api
        api().directory(path)
        return
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    check_private(path, directory=True)


def open_lock(path):
    require('runtime_lock')
    if platform_name() == 'windows':
        from graph_windows_native import ExclusiveLock
        return ExclusiveLock(path)
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        check_private(path)
        return os.fdopen(fd, 'a+')
    except BaseException:
        os.close(fd)
        raise


def prepare_state(path):
    private_directory(path)
    if platform_name() in ('macos', 'windows'):
        for name in ('watcher.lock', 'update.lock', 'stop-request', 'coordinator.jsonl',
                     'watcher-launch.json', 'run-disposition.json', 'dependency-wakes.json', 'runner.log'):
            if platform_name() == 'windows' and name in ('watcher.lock', 'update.lock'):
                continue  # An acquired exclusive handle cannot be reopened for inspection.
            file = path / name
            file_target(file)
            if file.exists() or file.is_symlink():
                check_private(file)


def file_target(path):
    if platform_name() == 'windows':
        from graph_windows_native import api
        api().no_reparse(path)
        if os.path.lexists(path):
            check_private(path)


def file_permissions(path):
    if platform_name() != 'windows':
        os.chmod(path, 0o600)
    check_private(path)


@contextmanager
def private_read(path, limit=8 * 1024 * 1024):
    if platform_name() == 'windows':
        # The protected parent excludes untrusted replacement. Revalidate both
        # open descriptor metadata and native owner/DACL before exposing bytes.
        check_private(path.parent, directory=True)
        check_private(path)
        with path.open('rb') as file:
            info = os.fstat(file.fileno())
            current = path.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit or (info.st_dev, info.st_ino) != (current.st_dev, current.st_ino):
                raise ValueError('Untrusted or oversized Windows evidence')
            check_private(path)
            yield file
        return
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('Untrusted or oversized local evidence')
        with os.fdopen(os.dup(fd), 'rb') as file:
            yield file
    finally:
        os.close(fd)


if __name__ == '__main__':
    print(json.dumps(capabilities()))
