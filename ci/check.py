"""Accounts-free payload/import/native-primitive check; no service or network."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    assert sys.version_info >= (3, 11), 'Python 3.11+ required'
    expected_arch = os.environ.get('EXPECT_ARCH')
    assert not expected_arch or platform.machine() == expected_arch, (platform.machine(), expected_arch)
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    expected = set(manifest['files']) | {'MANIFEST.json'}
    # A future independent repo has its own .git; never follow or validate its history here.
    actual = set()
    directories = {parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path('.')}
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if relative.parts[0] == '.git':
            continue
        assert not path.is_symlink(), str(relative)
        if path.is_dir():
            assert relative.as_posix() in directories, str(relative)
        else:
            actual.add(relative.as_posix())
    assert actual == expected, sorted(actual ^ expected)
    for name, record in manifest['files'].items():
        path = ROOT / name
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], name
        if os.name != 'nt':
            assert path.stat().st_mode & 0o777 == int(record['mode'], 8), name
        if name.endswith('.py'):
            compile(path.read_bytes(), name, 'exec')
    with tempfile.TemporaryDirectory(prefix='Community CI spaces ') as temporary:
        home = Path(temporary)
        env = {key: value for key, value in os.environ.items()
               if key in ('PATH', 'SystemRoot', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TEMP', 'TMP', 'LANG')}
        env.update(HOME=str(home), USERPROFILE=str(home), LOCALAPPDATA=str(home / 'local'),
                   VEZRYN_GRAPH_CONFIG=str(home / 'config/repos.toml'), VEZRYN_GRAPH_STATE=str(home / 'state'),
                   VEZRYN_GRAPH_LIBRARY=str(home / 'library'), PYTHONDONTWRITEBYTECODE='1',
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_CEILING_DIRECTORIES=str(ROOT.parent))
        for args in (['-c', 'import watcher,library,graph_platform,graph_update,graph_macos,graph_windows,graph_windows_native'],
                     ['watcher.py', 'capabilities'], ['watcher.py', 'repo', 'list'],
                     ['graph_update.py', 'version', '--json'], ['smoke.py']):
            subprocess.run([sys.executable, '-B', *args], cwd=ROOT, env=env, check=True, timeout=30)
    print(json.dumps({'local_check': 'PASS', 'os': platform.platform(), 'arch': platform.machine(),
                      'python': platform.python_version(), 'files': len(expected),
                      'manifest_sha256': hashlib.sha256((ROOT / 'MANIFEST.json').read_bytes()).hexdigest(),
                      'native_client_hooks_remote_pr': 'not tested'}))


if __name__ == '__main__':
    main()
