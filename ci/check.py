"""Accounts-free payload/import/native-primitive check; no service or network."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


# Deliberate positive source allowlist, independent of the mutable hash manifest.
# Add only source paths reviewed for this package; never glob private producer trees.
PAYLOAD_FILES = frozenset({
    '.codex/hooks.json',
    '.codex/hooks/lifecycle.py',
    'AGENTS.md',
    'ARCHITECTURE.md',
    'CONTRIBUTING.md',
    'IMPORT.md',
    'LICENSE',
    'LICENSE-REVIEW.md',
    'PLATFORMS.md',
    'QUICKSTART.md',
    'README.md',
    'RELEASE-NOTES-v0.1.0.md',
    'RELEASE-NOTES-v0.1.1.md',
    'SECURITY.md',
    'SMOKE-MATRIX.md',
    'bin/graph',
    'ci/check.py',
    'ci/archive.py',
    'ci/test_archive.py',
    'ci/test_update.py',
    'ci/smoke.yml.example',
    'ci/test_library.py',
    'ci/test_doctor.py',
    'ci/test_queue.py',
    'ci/test_first_issue.py',
    'ci/test_enrollment.py',
    'ci/test_linux_profile.py',
    'docs/GUIDANCE-REVIEW.md',
    'docs/LIBRARY.md',
    'docs/wiki/Community-and-Upkeep.md',
    'docs/wiki/Enrollment-and-Readiness.md',
    'docs/wiki/First-Workflow.md',
    'docs/wiki/Home.md',
    'docs/wiki/Playbooks-and-Skills.md',
    'docs/wiki/Troubleshooting-and-Recovery.md',
    'docs/wiki/_Sidebar.md',
    'examples/first-issue/ISSUE.md',
    'examples/first-issue/README.md',
    'examples/first-issue/greet.py',
    'examples/first-issue/test_greet.py',
    'graph_macos.py',
    'graph_platform.py',
    'graph_update.py',
    'graph_windows.py',
    'graph_windows_native.py',
    'library.py',
    'playbooks/architecture-decision.md',
    'playbooks/autonomous-issue-to-pr.md',
    'playbooks/benchmark-and-optimize.md',
    'playbooks/context-handoff.md',
    'playbooks/diagnose-and-repair.md',
    'playbooks/document-and-verify.md',
    'playbooks/implement-and-deliver.md',
    'playbooks/independent-review.md',
    'playbooks/integrate-and-verify.md',
    'playbooks/investigate-and-recommend.md',
    'playbooks/issue-triage.md',
    'playbooks/launch-and-observe.md',
    'playbooks/maintain-and-refactor.md',
    'playbooks/orchestrate-work.md',
    'playbooks/pause-and-recover.md',
    'playbooks/pr-maintenance.md',
    'playbooks/prepare-draft-pr.md',
    'playbooks/rapid-prototype.md',
    'playbooks/release-and-disposition.md',
    'playbooks/repair-and-resume.md',
    'playbooks/smoke-test.md',
    'playbooks/worktree-retirement.md',
    'policies/DELEGATION.md',
    'policies/ENGINEERING.md',
    'policies/ISSUE_LIFECYCLE.md',
    'policies/ISSUE_SELECTION.md',
    'policies/MODEL_ROUTING.md',
    'policies/ROUTING_MATRIX.md',
    'skills/agent-orchestration/SKILL.md',
    'skills/change-aware-verification/SKILL.md',
    'skills/context-continuity/SKILL.md',
    'skills/execution-intent-preservation/SKILL.md',
    'skills/independent-engineering-review/SKILL.md',
    'skills/observable-progress/SKILL.md',
    'skills/outcome-driven-engineering/SKILL.md',
    'skills/prototype-first/SKILL.md',
    'skills/repair-and-resume/SKILL.md',
    'skills/source-custody/SKILL.md',
    'smoke.py',
    'watcher.py',
})
PUBLIC_ROOT = '4c3bb369b5c7cff7f9b45c56c8d373294a87aa67'


def check_content(name, content):
    patterns = (rb'/' + rb'home/', rb'/' + rb'Users/',
                rb'gh' + rb'p_[A-Za-z0-9]{20,}', rb'github' + rb'_pat_[A-Za-z0-9_]{20,}',
                rb'-----BEGIN ' + rb'(?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    assert not any(re.search(pattern, content) for pattern in patterns), 'Private marker: ' + name
    repositories = re.findall(rb'Vezryn' + rb'-LLC/([A-Za-z0-9_.-]+)', content)
    assert all(repo.rstrip(b'.') in (b'graph-community', b'graph-community.git')
               for repo in repositories), 'Nonpublic repository marker: ' + name


def check_history(root):
    # A history-free archive has no Git evidence, rather than invented clean ancestry.
    if not (root / '.git').exists():
        return 'not present (archive); ancestry not checked'
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    def git(*args):
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args],
                                       env=env, text=True, stderr=subprocess.PIPE).strip()
    assert Path(git('rev-parse', '--show-toplevel')).resolve() == root.resolve(), 'Foreign containing repository'
    common = Path(git('rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = root / common
    assert not (common / 'objects/info/alternates').exists(), 'Git alternates forbidden'
    assert not (common / 'info/grafts').exists(), 'Git grafts forbidden'
    assert not git('for-each-ref', '--format=%(refname)', 'refs/replace'), 'Git replacement refs forbidden'
    roots = set(git('rev-list', '--max-parents=0', '--all').splitlines())
    assert roots == {PUBLIC_ROOT}, 'Unexpected Git roots; preserve independent public history'
    return 'PASS: independent public root, no alternates/grafts/replace refs'


def check_links(root, names):
    count = 0
    for name in names:
        if not name.endswith('.md'):
            continue
        text = (root / name).read_text()
        for target in re.findall(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)', text):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            if not target:
                continue
            destination = (root / name).parent / target
            assert destination.resolve().is_relative_to(root.resolve()), (name, target)
            assert destination.exists(), ('Missing local documentation target', name, target)
            count += 1
    return count


def check_payload(root):
    """Validate the reviewed source payload and return its exact file bytes."""
    manifest_path = root / 'MANIFEST.json'
    assert not manifest_path.is_symlink() and manifest_path.is_file(), 'Invalid manifest file'
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    contents = {'MANIFEST.json': manifest_bytes}
    check_content('MANIFEST.json', manifest_bytes)
    assert set(manifest['files']) == PAYLOAD_FILES, sorted(set(manifest['files']) ^ PAYLOAD_FILES)
    expected = PAYLOAD_FILES | {'MANIFEST.json'}
    # Only the checkout's own Git entry is excluded from source payload traversal.
    actual = set()
    directories = {parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path('.')}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if relative.parts[0] == '.git':
            continue
        assert not path.is_symlink(), str(relative)
        if path.is_dir():
            assert relative.as_posix() in directories, str(relative)
        else:
            assert stat.S_ISREG(path.stat().st_mode), str(relative)
            actual.add(relative.as_posix())
    assert actual == expected, sorted(actual ^ expected)
    for name, record in manifest['files'].items():
        path = root / name
        content = path.read_bytes()
        assert path.is_file() and hashlib.sha256(content).hexdigest() == record['sha256'], name
        if os.name != 'nt':
            assert path.stat().st_mode & 0o777 == int(record['mode'], 8), name
        check_content(name, content)
        if name.endswith('.py'):
            compile(content, name, 'exec')
        contents[name] = content
    return contents


def main():
    assert sys.version_info >= (3, 11), 'Python 3.11+ required'
    expected_arch = os.environ.get('EXPECT_ARCH')
    assert not expected_arch or platform.machine() == expected_arch, (platform.machine(), expected_arch)
    expected = set(check_payload(ROOT))
    history = check_history(ROOT)
    links = check_links(ROOT, expected)
    with tempfile.TemporaryDirectory(prefix='Community CI spaces ') as temporary:
        home = Path(temporary)
        env = {key: value for key, value in os.environ.items()
               if key in ('PATH', 'SystemRoot', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TEMP', 'TMP', 'LANG')}
        env.update(HOME=str(home), USERPROFILE=str(home), LOCALAPPDATA=str(home / 'local'),
                   VEZRYN_GRAPH_CONFIG=str(home / 'config/repos.toml'), VEZRYN_GRAPH_STATE=str(home / 'state'),
                   VEZRYN_GRAPH_LIBRARY=str(home / 'library'), PYTHONDONTWRITEBYTECODE='1',
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_CEILING_DIRECTORIES=str(ROOT.parent))
        for args in (['-c', 'import watcher,library,graph_platform,graph_update,graph_macos,graph_windows,graph_windows_native'],
                     ['watcher.py', 'capabilities'], ['watcher.py', 'doctor', '--json'], ['watcher.py', 'repo', 'list'],
                     ['graph_update.py', 'version', '--json'], ['smoke.py'],
                     ['-m', 'unittest', 'discover', '-s', 'ci', '-p', 'test_*.py', '-v']):
            subprocess.run([sys.executable, '-B', *args], cwd=ROOT, env=env, check=True, timeout=30)
    print(json.dumps({'local_check': 'PASS', 'os': platform.platform(), 'arch': platform.machine(),
                      'python': platform.python_version(), 'files': len(expected),
                      'manifest_sha256': hashlib.sha256((ROOT / 'MANIFEST.json').read_bytes()).hexdigest(),
                      'local_document_links': links, 'git_history': history,
                      'native_client_hooks_remote_pr': 'not tested'}))


if __name__ == '__main__':
    main()
