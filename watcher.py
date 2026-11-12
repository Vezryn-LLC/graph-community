#!/usr/bin/env python3
"""Tiny GitHub watcher that wakes one native Codex coordinator."""
from __future__ import annotations

import argparse
import calendar
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import platform as host_platform
import re
import shlex
import stat
import subprocess
import sys
import time
import tomllib

import graph_platform as platform

from library import explain as library_explain, instructions as library_instructions, resolve as library_resolve

ROOT = Path(__file__).resolve().parent
CONFIG, STATE = platform.paths()
STOP_REQUEST = STATE / "stop-request"
REF = re.compile(r"(?:https://github\.com/)?([A-Za-z0-9-]+/[A-Za-z0-9_.-]+)(?:#|/issues/)([0-9]+)")
PR_REF = re.compile(r"https://github\.com/([A-Za-z0-9-]+/[A-Za-z0-9_.-]+)/pull/([0-9]+)")
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]+\Z")


def doctor() -> dict:
    """Inspect local prerequisites only; never execute tools or prepare state."""
    capabilities = platform.capabilities()
    try:
        launcher = platform.executable('codex')
        if platform.platform_name() == 'windows':
            with Path(launcher).open('rb') as file:
                if file.read(2) != b'MZ':
                    raise ValueError('Not a native Windows executable')
        native = {'status': 'available', 'diagnostic': 'Native launcher resolved; not executed or authenticated'}
    except (OSError, ValueError, RuntimeError):
        native = {'status': 'unavailable', 'diagnostic': 'Put a supported native Codex executable on PATH; script wrappers may be unsupported'}

    # Do not use enrolled(): preflight must safely reject linked, oversized,
    # foreign-owned or permissive config rather than expose names or raw errors.
    try:
        with platform.private_read(CONFIG) as file:
            data = tomllib.load(file)
        repos = data.get('repositories', [])
        if not isinstance(repos, list) or not all(isinstance(repo, str) for repo in repos):
            raise ValueError('Invalid repository list')
        for repo in repos:
            validate_repo(repo)
        if len({repo.lower() for repo in repos}) != len(repos):
            raise ValueError('Duplicate repository')
        config = {'status': 'available', 'repository_count': len(repos)}
    except FileNotFoundError:
        config = {'status': 'not_configured', 'repository_count': None,
                  'diagnostic': 'No readable configuration found; no enrollment created'}
    except (OSError, ValueError, RuntimeError):
        config = {'status': 'unknown', 'repository_count': None,
                  'diagnostic': 'Configuration unreadable, unsafe or invalid; contents withheld'}

    try:
        overrides = Path(os.environ.get('VEZRYN_GRAPH_LIBRARY', str(CONFIG.parent / 'library'))).expanduser()
        if (overrides.exists() or overrides.is_symlink()) and not overrides.is_dir():
            raise ValueError('Override location is not a directory')
        effective = library_resolve(ROOT, overrides)
        required = ('ISSUE_SELECTION', 'ISSUE_LIFECYCLE', 'ENGINEERING',
                    'MODEL_ROUTING', 'ROUTING_MATRIX', 'DELEGATION')
        readable = {name for name, path in effective.items() if path.is_file() and os.access(path, os.R_OK)}
        library = {'status': 'available' if len(readable) == len(effective) else 'unavailable',
                   'effective_entries': len(effective), 'readable_entries': len(readable),
                   'required_policies': {name: f'policies/{name}.md' in readable for name in required},
                   'overrides': 'present' if overrides.is_dir() else 'absent (bundled guidance applies)'}
        if not all(library['required_policies'].values()):
            library['status'] = 'unavailable'
    except (OSError, ValueError, RuntimeError):
        library = {'status': 'unknown', 'diagnostic': 'Effective library unavailable; inspect local override configuration privately'}

    return {'schema_version': 1,
            'python': {'version': host_platform.python_version(), 'supported': sys.version_info >= (3, 11)},
            'os': {'name': capabilities['platform'], 'release': host_platform.release()},
            'prerequisites': {name: capabilities['prerequisites'][name] for name in ('git', 'gh', 'codex')},
            'native_codex': native, 'configuration': config, 'library': library,
            'platform': capabilities,
            'limits': 'Local read-only preflight; authentication, permissions, trusted hooks, worker delivery and native-host qualification NOT checked'}


def print_doctor(as_json=False):
    report = doctor()
    if as_json:
        print(json.dumps(report, indent=2))
        return
    print(f"Python {report['python']['version']} | OS {report['os']['name']} {report['os']['release']}")
    for name, found in report['prerequisites'].items():
        print(f"{name}: {'found on PATH' if found else 'missing from PATH'}")
    print(f"Codex native launcher: {report['native_codex']['status']} — {report['native_codex']['diagnostic']}")
    config = report['configuration']
    print(f"Configuration: {config['status']} | repository count: {config['repository_count']}")
    if 'diagnostic' in config:
        print(config['diagnostic'])
    print('Effective library: ' + json.dumps(report['library']))
    print('Platform qualification: ' + report['platform']['qualification'])
    for name, value in report['platform']['capabilities'].items():
        print(f"  {name}: {'available' if value['available'] else 'unavailable'}" +
              (f" — {value['diagnostic']}" if value['diagnostic'] else ''))
    print(report['limits'])


def validate_repo(name: str) -> str:
    if not REPO.fullmatch(name):
        raise ValueError("Repository must be owner/name, e.g. example/project")
    return name


def enrolled() -> list[str]:
    if not CONFIG.exists():
        return []
    if platform.platform_name() == 'windows':
        platform.check_private(CONFIG.parent, directory=True)
    platform.check_private(CONFIG)
    with CONFIG.open("rb") as file:
        data = tomllib.load(file)
    repos = data.get("repositories", [])
    if not isinstance(repos, list) or not all(isinstance(r, str) for r in repos):
        raise ValueError(f"Invalid repositories in {CONFIG}")
    for repo in repos:
        validate_repo(repo)
    if len({repo.lower() for repo in repos}) != len(repos):
        raise ValueError(f"Duplicate repositories in {CONFIG}")
    return repos


def save(repos: list[str]) -> None:
    platform.require("private_state")
    platform.private_directory(CONFIG.parent)
    tmp = CONFIG.with_name(CONFIG.name + f".{os.getpid()}.tmp")
    platform.file_target(CONFIG)
    platform.file_target(tmp)
    created = False
    try:
        with tmp.open("x", encoding="utf-8") as file:
            created = True
            platform.file_permissions(tmp)
            file.write("repositories = [\n")
            for repo in repos:
                file.write(f"  {json.dumps(repo)},\n")
            file.write("]\n")
        os.replace(tmp, CONFIG)
    finally:
        if created:
            tmp.unlink(missing_ok=True)


def manage(action: str, repo: str | None) -> None:
    if action == "list":
        current = enrolled()
        print("\n".join(current) if current else "(no enrolled repositories)")
        return
    assert repo is not None
    validate_repo(repo)
    platform.private_directory(CONFIG.parent)
    # Keep a stable lock inode beside the config: replacing/deleting the lock
    # would let another editor acquire different ownership during this write.
    with platform.open_lock(CONFIG.with_name(CONFIG.name + ".lock")) as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError as error:
            raise RuntimeError("Enrollment is being edited; retry the repo command after the other editor finishes") from error
        current = enrolled()
        match = {item.lower(): item for item in current}
        if action == "add" and repo.lower() not in match:
            current.append(repo)
        if action == "revoke":
            current = [item for item in current if item.lower() != repo.lower()]
        save(current)
    print(f"{action}: {repo} ({len(current)} enrolled)")


LIFECYCLE_LABELS = ('status:ready', 'status:in-progress', 'status:awaiting-merge', 'status:blocked')


def repo_read(endpoint):
    """Explicit GET through the existing gh integration; errors never escape raw."""
    try:
        return github('api', '--method', 'GET', endpoint), 'available'
    except subprocess.CalledProcessError as error:
        text = str(error.stderr or '').lower()
        if 'rate limit' in text or 'http 429' in text:
            status = 'rate_limited'
        elif 'http 401' in text or 'http 403' in text:
            status = 'access_denied'
        elif 'http 404' in text:
            status = 'unavailable_or_not_found'
        else:
            status = 'unavailable'
        return None, status
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    except (OSError, ValueError, RuntimeError):
        return None, 'unavailable'


def repo_check_report(repository=None):
    report = {'schema_version': 1, 'source': 'Authenticated GitHub gh api GET',
              'complete': True, 'repositories': [],
              'limits': 'Read snapshot only; successful reads do not establish write/merge authority or issue eligibility. No enrollment, label changes or dispatch.'}
    try:
        repos = [validate_repo(repository)] if repository is not None else enrolled()
        report['targets'] = 'explicit' if repository is not None else 'enrolled'
    except (OSError, ValueError, RuntimeError):
        report.update(complete=False, diagnostic='Repository target or enrollment unavailable, unsafe or invalid; inspect privately')
        repos = []
    for repo in repos:
        entry = {'repository': repo, 'metadata': {'status': 'unavailable'},
                 'label_read': {'status': 'unavailable'},
                 'labels': {label: 'unknown' for label in LIFECYCLE_LABELS}}
        metadata, status = repo_read(f'repos/{repo}')
        if status == 'available':
            if (not isinstance(metadata, dict) or not isinstance(metadata.get('full_name'), str)
                    or not REPO.fullmatch(metadata['full_name'])
                    or metadata['full_name'].lower() != repo.lower()
                    or not all(type(metadata.get(key)) is bool for key in ('private', 'archived', 'disabled', 'has_issues'))):
                status = 'invalid_response'
            else:
                entry['metadata'].update({key: metadata[key] for key in ('full_name', 'private', 'archived', 'disabled', 'has_issues')})
                permissions = metadata.get('permissions', {})
                entry['metadata']['reported_permissions'] = {key: permissions[key] for key in ('pull', 'push', 'admin', 'maintain', 'triage')
                    if isinstance(permissions, dict) and type(permissions.get(key)) is bool}
        entry['metadata']['status'] = status
        found = set()
        # At most ten 100-label pages; reaching the cap remains unknown, never missing.
        for page in range(1, 11):
            labels, status = repo_read(f'repos/{repo}/labels?per_page=100&page={page}')
            if status != 'available':
                break
            if (not isinstance(labels, list) or len(labels) > 100
                    or not all(isinstance(label, dict) and isinstance(label.get('name'), str) for label in labels)):
                status = 'invalid_response'
                break
            found.update(label['name'] for label in labels)
            if len(labels) < 100:
                break
        else:
            status = 'incomplete'
        entry['label_read']['status'] = status
        entry['labels'] = {label: 'present' if label in found else 'missing' if status == 'available' else 'unknown'
                           for label in LIFECYCLE_LABELS}
        if entry['metadata']['status'] != 'available' or status != 'available':
            entry['status'] = 'read_failed'
        elif 'missing' in entry['labels'].values():
            entry['status'] = 'missing_labels'
        else:
            entry['status'] = 'configured_readable'
        report['complete'] = report['complete'] and entry['status'] == 'configured_readable'
        report['repositories'].append(entry)
    return report


def print_repo_check(repository=None, as_json=False):
    report = repo_check_report(repository)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(report['source'])
        print(report['limits'])
        if 'diagnostic' in report:
            print(report['diagnostic'])
        elif not report['repositories']:
            print('No enrolled repositories; supply an explicit owner/name or deliberately enroll one')
        for entry in report['repositories']:
            print(f"{entry['repository']}: {entry['status']}")
            print('  Metadata: ' + json.dumps(entry['metadata']))
            print('  Label read: ' + entry['label_read']['status'])
            for label, status in entry['labels'].items():
                print(f'  {label}: {status}')
        print('For failed reads, check gh installation/authentication and repository access privately; for missing labels, use the manual gh label create commands in QUICKSTART.md')
    return 0 if report['complete'] else 1


def ready_metadata(repo: str) -> list[dict]:
    """Shared read-only ready-label source; never fetch bodies or comments."""
    result = subprocess.run(
        [platform.executable("gh"), "issue", "list", "--repo", repo, "--state", "open",
         "--label", "status:ready", "--limit", "1000",
         "--json", "number,updatedAt,labels"],
        capture_output=True, text=True, timeout=60, check=True,
    )
    issues = json.loads(result.stdout)
    if not isinstance(issues, list):
        raise ValueError("GitHub issue response was not a list")
    for issue in issues:
        if (not isinstance(issue, dict) or type(issue.get("number")) is not int
                or issue["number"] < 1 or not isinstance(issue.get("updatedAt"), str)
                or not isinstance(issue.get("labels"), list)
                or not all(isinstance(label, dict) and isinstance(label.get("name"), str)
                           for label in issue["labels"])):
            raise ValueError("Unexpected issue data")
    return issues


def backlog(repositories: list[str]) -> tuple[list[dict], int]:
    """Only fetch issue metadata. Codex owns all task-selection decisions."""
    results, failures = [], 0
    for repo in repositories:
        try:
            for issue in ready_metadata(repo):
                labels = {label["name"] for label in issue["labels"]}
                if "status:ready" not in labels or labels.intersection(
                        {"status:blocked", "status:in-progress", "status:awaiting-merge"}):
                    continue
                results.append({"repo": repo, "number": issue["number"], "updatedAt": issue["updatedAt"]})
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as error:
            failures += 1
            print(f"GitHub check failed for {repo}: {error}", file=sys.stderr, flush=True)
    return results, failures


def queue_report() -> dict:
    """User-invoked metadata snapshot, without watcher state or eligibility inference."""
    report = {'schema_version': 1, 'source': 'GitHub gh issue list (open, status:ready)',
              'complete': True, 'repositories': [],
              'limits': 'READY_LABEL_CANDIDATE only; ownership, dependencies, blocked comments and recovery/source gates are not evaluated'}
    try:
        repos = enrolled()
    except (OSError, ValueError, RuntimeError):
        report.update(complete=False, configuration='unavailable',
                      diagnostic='Enrollment unreadable, unsafe or invalid; inspect configuration privately')
        repos = []
    else:
        report['configuration'] = 'available' if repos else 'no_enrolled_repositories'
    for repo in repos:
        entry = {'repository': repo, 'status': 'failed', 'candidates': [], 'observed_at': None,
                 'source_age_seconds': None}
        try:
            issues = ready_metadata(repo)
            entry['observed_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            entry['status'] = 'incomplete' if len(issues) >= 1000 else 'complete'
            if entry['status'] == 'incomplete':
                entry['diagnostic'] = 'Read reached the 1000-issue limit; more candidates may exist'
            for issue in issues:
                labels = {label['name'] for label in issue['labels']}
                if 'status:ready' in labels:
                    entry['candidates'].append({'number': issue['number'], 'updated_at': issue['updatedAt'],
                        'classification': 'READY_LABEL_CANDIDATE',
                        'lifecycle_labels': sorted(labels & {'status:ready', 'status:blocked',
                                                           'status:in-progress', 'status:awaiting-merge'})})
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
            # Raw tool errors may contain paths, credentials or server response text.
            entry['diagnostic'] = 'GitHub metadata unavailable; check gh installation, authentication and repository access privately'
        report['repositories'].append(entry)
        if entry['status'] != 'complete':
            report['complete'] = False
    report['generated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    for entry in report['repositories']:
        if entry['observed_at']:
            entry['source_age_seconds'] = max(0, int(time.time() - calendar.timegm(
                time.strptime(entry['observed_at'], '%Y-%m-%dT%H:%M:%SZ'))))
    return report


def print_queue(as_json=False) -> int:
    report = queue_report()
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Queue snapshot: {report['generated_at']} | {'complete' if report['complete'] else 'INCOMPLETE'}")
        print('Source: ' + report['source'])
        print(report['limits'])
        if 'diagnostic' in report:
            print(report['diagnostic'])
        elif not report['repositories']:
            print('No enrolled repositories; use repo add owner/name to enroll one')
        for entry in report['repositories']:
            count = 'candidate count unknown' if entry['status'] == 'failed' else f"{len(entry['candidates'])} candidates"
            print(f"{entry['repository']}: {entry['status']} | {count}" +
                  (f" | source {entry['observed_at']} (age {entry['source_age_seconds']}s)" if entry['observed_at'] else ''))
            for candidate in entry['candidates']:
                print(f"  #{candidate['number']} READY_LABEL_CANDIDATE | updated {candidate['updated_at']} | " +
                      ', '.join(candidate['lifecycle_labels']))
            if 'diagnostic' in entry:
                print('  ' + entry['diagnostic'])
    return 0 if report['complete'] else 1


def github(*args: str):
    result = subprocess.run([platform.executable("gh"), *args], capture_output=True, text=True,
                            timeout=60, check=True)
    return json.loads(result.stdout)


DEPENDENCY_OPEN = '<!-- graph-dependencies -->'
DEPENDENCY_CLOSE = '<!-- /graph-dependencies -->'
CONNECTION = 'totalCount pageInfo{hasNextPage endCursor} nodes'
COMMENTS = 'comments(first:100){' + CONNECTION + '{body}}'
PARENT_QUERY = '''query($owner:String!,$name:String!,$cursor:String) {
 repository(owner:$owner,name:$name) { issues(first:100,after:$cursor,states:OPEN,labels:["status:blocked"]) {
 totalCount pageInfo{hasNextPage endCursor} nodes { number body
 labels(first:100){totalCount pageInfo{hasNextPage endCursor} nodes{name}}
 COMMENTS NATIVE } } } }'''.replace('COMMENTS', COMMENTS)
REVERSE_QUERY = '''query($search:String!,$cursor:String) {
 search(query:$search,type:ISSUE,first:100,after:$cursor) {
 issueCount pageInfo{hasNextPage endCursor} nodes { ... on Issue { number body COMMENTS } } } }'''.replace('COMMENTS', COMMENTS)
CHILD_QUERY = '''query($owner:String!,$name:String!,$number:Int!) {
 repository(owner:$owner,name:$name) { issue(number:$number) { state stateReason body COMMENTS
 closedByPullRequestsReferences(first:100){totalCount pageInfo{hasNextPage endCursor} nodes{url}} } } }'''.replace('COMMENTS', COMMENTS)


def reference(value: str) -> tuple[str, int] | None:
    """One literal issue reference, never a partial regex match."""
    if not isinstance(value, str) or len(value) > 2048:
        return None
    match = re.fullmatch(r'(?:https://github\.com/([^/]+/[^/]+)/issues/([1-9][0-9]*)|([^\s#]+/[^\s#]+)#([1-9][0-9]*))', value)
    if not match:
        return None
    repo, number = (match[1], match[2]) if match[1] else (match[3], match[4])
    try:
        return validate_repo(repo).lower(), int(number)
    except ValueError:
        return None


def dependency_declaration(body: str) -> dict:
    """The optional body declaration overrides history, including explicit None."""
    if not isinstance(body, str):
        return {'mode': 'unknown', 'refs': None, 'diagnostics': ['parent_body_unavailable']}
    reserved = re.findall(r'<!--\s*/?\s*graph-dependenc[^\n]*', body, re.I)
    if not reserved:
        return {'mode': 'legacy', 'refs': None, 'diagnostics': []}
    lines = body.splitlines()
    fence, ambiguous = None, False
    for line in lines:
        marker = re.search(r'<!--\s*/?\s*graph-dependenc', line, re.I)
        if marker and (fence or line.startswith('\t') or len(line) - len(line.lstrip(' ')) >= 4):
            ambiguous = True
        code = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if code:
            if fence is None:
                fence = code[1]
            elif code[1][0] == fence[0] and len(code[1]) >= len(fence) and not code[2].strip():
                fence = None
    starts = [i for i, line in enumerate(lines) if line.strip() == DEPENDENCY_OPEN]
    ends = [i for i, line in enumerate(lines) if line.strip() == DEPENDENCY_CLOSE]
    invalid = ambiguous or len(reserved) != 2 or len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]
    content = [line.strip() for line in lines[starts[0] + 1:ends[0]]] if not invalid else []
    content = [line for line in content if line]
    refs = set()
    if not invalid and content == ['None']:
        return {'mode': 'none', 'refs': refs, 'diagnostics': []}
    if not content:
        invalid = True
    for line in content:
        match = re.fullmatch(r'Blocked by\s*:?\s+(.+)', line, re.I)
        if not match:
            invalid = True
            continue
        parts = re.split(r'\s*,\s*|\s+', match[1].strip())
        for part in parts:
            item = reference(part)
            if item is None or item in refs:
                invalid = True
            else:
                refs.add(item)
    if invalid:
        # Hash only declaration-like content, never put raw issue prose in wake receipts.
        positions = [i for i, line in enumerate(lines) if re.search(r'<!--\s*/?\s*graph-dependenc', line, re.I)]
        last = max(positions) + 1 if len(positions) > 1 else len(lines)
        marked = '\n'.join(line.strip() for line in lines[min(positions):last])
        return {'mode': 'invalid', 'refs': None, 'diagnostics': ['invalid_current_declaration'],
                'declaration_fingerprint': hashlib.sha256(marked.encode()).hexdigest()[:16]}
    return {'mode': 'references', 'refs': refs, 'diagnostics': []}


def connection(value: object) -> tuple[list, bool]:
    if not isinstance(value, dict) or not isinstance(value.get('nodes'), list):
        return [], False
    count, page = value.get('totalCount'), value.get('pageInfo')
    complete = type(count) is int and count == len(value['nodes']) and isinstance(page, dict) and page.get('hasNextPage') is False
    return value['nodes'], complete


def legacy_links(issue: dict, direction: str) -> tuple[set, bool]:
    """Compatibility discovery is a lower bound when prose/comments are incomplete."""
    refs, complete = set(), isinstance(issue.get('body'), str)
    comments, all_comments = connection(issue.get('comments'))
    complete = complete and all_comments
    texts = [issue.get('body', '')]
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get('body'), str):
            complete = False
        else:
            texts.append(comment['body'])
    for text in texts:
        if not isinstance(text, str):
            continue
        for line in text.splitlines():
            match = re.search(re.escape(direction) + r'\s*:?\s*(.*)', line, re.I)
            if not match:
                continue
            found = list(REF.finditer(match[1]))
            usable = []
            for ref in found:
                # A trailing letter/slash is a malformed reference, not issue 12 of #12oops.
                if ref.end() < len(match[1]) and (match[1][ref.end()].isalnum() or match[1][ref.end()] in '/_'):
                    complete = False
                    continue
                item = reference(ref[0])
                if item:
                    refs.add(item)
                    usable.append(ref.span())
                else:
                    complete = False
            rest = match[1]
            for start, end in reversed(usable):
                rest = rest[:start] + ' ' * (end - start) + rest[end:]
            if not usable or re.search(r'github\.com/|[\w.-]+/[\w.-]+(?:#|/issues/)|#[\w]+', rest):
                complete = False
    return refs, complete


class NativeDependencyUnsupported(ValueError):
    pass


def unsupported_dependency_field(value: object) -> bool:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return False
    errors = value.get('errors') if isinstance(value, dict) else None
    if not isinstance(errors, list) or not errors:
        return False
    for error in errors:
        if not isinstance(error, dict):
            return False
        ext = error.get('extensions') or {}
        if not isinstance(ext, dict):
            return False
        typed = ext.get('code') == 'undefinedField' and ext.get('typeName') == 'Issue' and ext.get('fieldName') == 'blockedBy'
        message = error.get('message')
        named = isinstance(message, str) and re.fullmatch(r"Field ['\"]blockedBy['\"] doesn't exist on type ['\"]Issue['\"]", message)
        if not typed and not named:
            return False
    return True


def dependency_query(query: str, native=False, **variables):
    args = ['api', 'graphql', '-f', 'query=' + query]
    for key, value in variables.items():
        if value is not None:
            args += ['-F' if type(value) is int else '-f', f'{key}={value}']
    try:
        result = github(*args)
    except subprocess.CalledProcessError as error:
        if native and unsupported_dependency_field(error.stdout):
            raise NativeDependencyUnsupported() from error
        raise
    if native and unsupported_dependency_field(result):
        raise NativeDependencyUnsupported()
    if not isinstance(result, dict) or not isinstance(result.get('errors', []), list) or result.get('errors') or not isinstance(result.get('data'), dict):
        raise ValueError('Incomplete dependency GraphQL response')
    return result['data']


def dependency_pages(repo: str, reverse=False, native=True) -> tuple[list, bool, bool]:
    owner, name = repo.split('/')
    query = REVERSE_QUERY if reverse else PARENT_QUERY.replace('NATIVE', 'blockedBy(first:100){' + CONNECTION + '{url}}' if native else '')
    rows, cursor, total = [], None, None
    for _ in range(10):
        try:
            variables = {'search': f'repo:{repo} is:issue "Unblocks" in:body,comments'} if reverse else {'owner': owner, 'name': name}
            data = dependency_query(query, native=native and not reverse, cursor=cursor, **variables)
        except NativeDependencyUnsupported:
            return dependency_pages(repo, reverse=False, native=False)
        repository = data.get('repository')
        page = data.get('search') if reverse else repository.get('issues') if isinstance(repository, dict) else None
        if not isinstance(page, dict) or not isinstance(page.get('nodes'), list):
            raise ValueError('Missing dependency index')
        count = page.get('issueCount' if reverse else 'totalCount')
        if type(count) is not int or count < 0 or total is not None and count != total:
            raise ValueError('Inconsistent dependency index')
        total = count
        incoming = page['nodes']
        if any(not isinstance(node, dict) or type(node.get('number')) is not int or node['number'] <= 0 for node in incoming):
            raise ValueError('Invalid indexed issue')
        if len({node['number'] for node in rows + incoming}) != len(rows) + len(incoming):
            raise ValueError('Duplicate indexed issues')
        rows.extend(incoming)
        info = page.get('pageInfo')
        if not isinstance(info, dict) or type(info.get('hasNextPage')) is not bool:
            raise ValueError('Missing dependency pagination')
        if info['hasNextPage'] is False:
            return rows, len(rows) == total, native
        next_cursor = info.get('endCursor')
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise ValueError('Invalid dependency cursor')
        cursor = next_cursor
    return rows, False, native


def ref_names(refs):
    return [f'{r}#{n}' for r, n in sorted(refs)]


def native_dependencies(issue, supported):
    if not supported:
        return {'read_status': 'unsupported', 'links': None, 'observed_links': []}, set()
    nodes, complete = connection(issue.get('blockedBy'))
    refs = set()
    for node in nodes:
        item = reference(node.get('url', '')) if isinstance(node, dict) else None
        if item is None or item in refs:
            complete = False
        else:
            refs.add(item)
    return {'read_status': 'complete' if complete else 'unknown', 'links': ref_names(refs) if complete else None,
            'observed_links': ref_names(refs)}, refs


def delivery(child_repo, child_number, enrolled_names, children, prs):
    name = f'{child_repo}#{child_number}'
    result = {'child': name, 'read_status': 'unknown', 'state': None, 'reason': None, 'merged_prs': []}
    if child_repo not in enrolled_names:
        result['read_status'] = 'unenrolled'
        return result
    try:
        key = child_repo, child_number
        if key not in children:
            owner, repo = child_repo.split('/')
            repository = dependency_query(CHILD_QUERY, owner=owner, name=repo, number=child_number).get('repository')
            children[key] = repository.get('issue') if isinstance(repository, dict) else None
        child = children[key]
        if not isinstance(child, dict) or child.get('state') not in {'OPEN', 'CLOSED'} or 'stateReason' not in child or child['stateReason'] not in {None, 'COMPLETED', 'NOT_PLANNED', 'REOPENED', 'DUPLICATE'}:
            raise ValueError('Invalid child metadata')
        result.update(state=child['state'], reason=child['stateReason'])
        comments, complete = connection(child.get('comments'))
        closing, all_closing = connection(child.get('closedByPullRequestsReferences'))
        complete = complete and all_closing and isinstance(child.get('body'), str)
        texts = [child.get('body', '')]
        refs = set()
        for node in closing:
            if not isinstance(node, dict) or not isinstance(node.get('url'), str) or not PR_REF.fullmatch(node['url']):
                complete = False
            else:
                refs.update((r.lower(), int(n)) for r, n in PR_REF.findall(node['url']))
        for comment in comments:
            if not isinstance(comment, dict) or not isinstance(comment.get('body'), str):
                complete = False
            else:
                texts.append(comment['body'])
        for text in texts:
            if isinstance(text, str):
                refs.update((r.lower(), int(n)) for r, n in PR_REF.findall(text))
        if len(refs) > 20:
            complete = False
        for pr_repo, number in sorted(refs)[:20]:
            if pr_repo not in enrolled_names:
                complete = False
                continue
            if (pr_repo, number) not in prs:
                prs[(pr_repo, number)] = github('pr', 'view', str(number), '--repo', pr_repo, '--json', 'mergedAt')
            pr = prs[(pr_repo, number)]
            if not isinstance(pr, dict) or 'mergedAt' not in pr or pr['mergedAt'] is not None and not isinstance(pr['mergedAt'], str):
                complete = False
            elif pr['mergedAt']:
                # GraphQL DateTime is explicit UTC/offset; malformed strings aren't merges.
                from datetime import datetime
                try:
                    at = datetime.fromisoformat(pr['mergedAt'].replace('Z', '+00:00'))
                    if at.tzinfo is None:
                        raise ValueError('Missing merge timezone')
                    result['merged_prs'].append(f'{pr_repo}#{number}')
                except ValueError:
                    complete = False
        result['read_status'] = 'complete' if complete else 'unknown'
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        pass
    return result


def stale_dependency(old):
    if not isinstance(old, dict):
        return None
    if old.get('status') == 'current':
        keys = ('mode', 'status', 'links', 'intended_links', 'native', 'evidence', 'diagnostics')
        return {'stale': True, 'observation': {k: old[k] for k in keys if k in old}}
    if 'status' not in old and isinstance(old.get('links'), list):
        refs = {item for value in old['links'][:100] if (item := reference(value)) is not None}
        return {'stale': True, 'observation': {'mode': 'legacy', 'status': 'legacy_receipt_unverified', 'links': ref_names(refs)}}
    return old.get('last_known_good')


def dependency_candidate(key, value):
    """Prompt payload is bounded; the coordinator rereads the complete parent."""
    out = {k: value.get(k) for k in ('mode', 'status', 'diagnostics', 'declaration_fingerprint', 'reference_fingerprint', 'intended_links_omitted') if k in value}
    out['parent' if not key.startswith('dependency-scan:') else 'repository'] = key.removeprefix('dependency-scan:')
    for field in ('links', 'intended_links', 'native_only_links'):
        links = value.get(field)
        out[field] = links[:10] if isinstance(links, list) else None
        if isinstance(links, list) and len(links) > 10:
            out[field + '_omitted'] = out.get(field + '_omitted', 0) + len(links) - 10
    out['native_read_status'] = (value.get('native') or {}).get('read_status')
    out['evidence'] = [dict(e, merged_prs=e.get('merged_prs', [])[:3]) for e in value.get('evidence', [])[:10]]
    out['evidence_omitted'] = max(0, len(value.get('evidence', [])) - 10)
    if value.get('last_known_good'):
        good = value['last_known_good']['observation']
        out['last_known_good'] = {'stale': True, 'links': (good.get('links') or [])[:10]}
    return out


def dependency_changes(repositories: list[str], previous: dict) -> tuple[dict, list[dict], int]:
    """Typed read-only observations; unknown/invalid are never empty dependency sets."""
    enrolled_names = {repo.lower() for repo in repositories}
    parents, current, children, prs, failures = {}, {}, {}, {}, 0
    for repo in repositories:
        repo = repo.lower()
        scope_key = 'dependency-scan:' + repo
        try:
            issues, complete, supported = dependency_pages(repo)
            if not complete:
                failures += 1
            current[scope_key] = {'status': 'current' if complete else 'unknown', 'diagnostics': [] if complete else ['parent_index_incomplete']}
            for issue in issues:
                if not isinstance(issue, dict) or type(issue.get('number')) is not int or issue['number'] <= 0:
                    raise ValueError('Invalid parent issue')
                key = f"{repo}#{issue['number']}"
                declaration = dependency_declaration(issue.get('body'))
                native, native_refs = native_dependencies(issue, supported)
                diagnostics = list(declaration['diagnostics'])
                labels, labels_complete = connection(issue.get('labels'))
                if not labels_complete or not any(isinstance(label, dict) and label.get('name') == 'status:blocked' for label in labels):
                    diagnostics.append('blocked_membership_unknown')
                if native['read_status'] == 'unknown':
                    diagnostics.append('native_dependencies_unknown')
                refs = declaration['refs']
                if declaration['mode'] == 'legacy':
                    refs, all_text = legacy_links(issue, 'Blocked by')
                    refs |= native_refs
                    if not all_text:
                        diagnostics.append('legacy_evidence_incomplete_or_malformed')
                parents[key] = {'mode': declaration['mode'], 'refs': refs, 'native': native, 'native_refs': native_refs,
                                'diagnostics': diagnostics, 'declaration_fingerprint': declaration.get('declaration_fingerprint')}
            if not complete:
                for key, old in previous.items():
                    if key.startswith(repo + '#') and key not in parents:
                        current[key] = {'mode': 'unknown', 'status': 'unknown', 'links': None, 'diagnostics': ['parent_index_incomplete'], 'last_known_good': stale_dependency(old)}
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
            failures += 1
            current[scope_key] = {'status': 'unknown', 'diagnostics': ['parent_read_unavailable_or_invalid']}
            for key in list(parents):
                if key.startswith(repo + '#'):
                    del parents[key]
            for key, old in previous.items():
                if key.startswith(repo + '#'):
                    current[key] = {'mode': 'unknown', 'status': 'unknown', 'links': None, 'diagnostics': ['parent_read_unavailable_or_invalid'], 'last_known_good': stale_dependency(old)}
    legacy = {key for key, value in parents.items() if value['mode'] == 'legacy'}
    if legacy:
        for repo in repositories:
            try:
                candidates, complete, _ = dependency_pages(repo.lower(), reverse=True)
                for child in candidates:
                    if not isinstance(child, dict) or type(child.get('number')) is not int or child['number'] <= 0:
                        raise ValueError('Invalid reverse issue')
                    links, all_text = legacy_links(child, 'Unblocks')
                    complete = complete and all_text
                    for parent in ref_names(links):
                        if parent in legacy:
                            parents[parent]['refs'].add((repo.lower(), child['number']))
                if not complete:
                    raise ValueError('Incomplete reverse discovery')
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
                failures += 1
                for key in legacy:
                    parents[key]['diagnostics'].append('reverse_evidence_unknown')
    for key, parent in parents.items():
        refs = parent['refs']
        if refs is not None and len(refs) > 100:
            parent['diagnostics'].append('dependency_reference_cap')
        evidence = [delivery(r, n, enrolled_names, children, prs) for r, n in sorted(refs or [])[:100]]
        diagnostics = parent['diagnostics']
        if any(e['read_status'] != 'complete' for e in evidence):
            diagnostics.append('dependency_delivery_unknown_or_unenrolled')
        native_only = parent['native_refs'] - (refs or set()) if parent['mode'] in {'references', 'none'} else set()
        if native_only:
            diagnostics.append('native_current_discrepancy')
        status = 'invalid' if parent['mode'] == 'invalid' else 'unknown' if any(code != 'native_current_discrepancy' for code in diagnostics) else 'discrepancy' if native_only else 'current'
        if status in {'unknown', 'invalid', 'discrepancy'}:
            failures += 1
        value = {'mode': parent['mode'], 'status': status, 'links': ref_names(refs or set()) if status == 'current' else None,
                 'intended_links': ref_names(refs)[:100] if refs is not None else None, 'intended_links_omitted': max(0, len(refs or []) - 100),
                 'reference_fingerprint': hashlib.sha256(json.dumps(ref_names(refs or [])).encode()).hexdigest()[:16],
                 'native': parent['native'], 'native_only_links': ref_names(native_only),
                 'evidence': evidence, 'diagnostics': sorted(set(diagnostics)), 'declaration_fingerprint': parent['declaration_fingerprint']}
        if status != 'current':
            value['last_known_good'] = stale_dependency(previous.get(key))
        current[key] = value
    changes = []
    for key, value in sorted(current.items()):
        old = previous.get(key)
        terminal = any(e.get('state') == 'CLOSED' or e.get('merged_prs') for e in value.get('evidence', []))
        first_signal = value.get('status') != 'current' or value.get('mode') in {'references', 'none'} or terminal
        if value != old and (old is not None or first_signal):
            changes.append(dependency_candidate(key, value))
    if len(changes) > 40:
        changes = changes[:39] + [{'status': 'reconciliation_scope_capped', 'omitted_candidates': len(changes) - 39,
                                  'repositories': sorted(enrolled_names)[:20], 'repositories_omitted': max(0, len(enrolled_names) - 20), 'diagnostics': ['reread_all_blocked_parents_in_scope']}]
    return current, changes, failures


def activation_source() -> dict:
    """Local running-source evidence, never proof that a task's gates are satisfied."""
    from graph_update import snapshot, git
    evidence = {}
    next_action = 'Inspect graph version and the actual service/process/source identity; finish draining or use the existing drain-first activation path, then reconcile preserved assignments. No unblock is established.'
    try:
        source = snapshot()
        evidence = {key: source[key] for key in ('service', 'installed', 'running', 'dirty', 'runningDirty',
                    'runtimeMatches', 'remote', 'remoteAt', 'remoteError', 'relation', 'comparedInstalled') if key in source}
        evidence['localRef'] = git('rev-parse', 'refs/remotes/origin/main')
        if not (source.get('service') == 'running' and source.get('tracking') is True
                and source.get('dirty') is False and source.get('runningDirty') is False
                and source.get('runtimeMatches') is True and source.get('running')
                and source['running'] == source.get('installed')):
            raise RuntimeError(source.get('diagnostic') or source.get('summary', 'Unknown running source'))
        if evidence['localRef'] != source['installed']:
            next_action = (f"Refresh only the tracking ref: git -C {shlex.quote(str(ROOT))} fetch --no-tags origin "
                           'refs/heads/main:refs/remotes/origin/main; then rerun graph check-update and graph status. '
                           'If fetch refuses or revisions still differ, inspect source ancestry; preserve assignments and do not reset or restart.')
            raise RuntimeError('Local origin/main differs from installed HEAD; it may be stale. Cached remote evidence does not refresh this ref or verify ancestry.')
        overrides = Path(os.environ.get('VEZRYN_GRAPH_LIBRARY', str(CONFIG.parent / 'library'))).expanduser()
        digest = hashlib.sha256()
        for name, path in library_resolve(ROOT, overrides).items():
            digest.update(json.dumps([name, str(path)]).encode())
            digest.update(path.read_bytes())
        guidance = digest.hexdigest()
        identity = hashlib.sha256(json.dumps([source['installed'], guidance]).encode()).hexdigest()
        return {'status': 'verified', 'identity': identity, 'running': source['running'],
                'checkout': str(ROOT), 'guidance': guidance, 'evidence': evidence}
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        return {'status': 'unverified', 'diagnostic': str(error)[:500],
                'next_action': next_action, 'evidence': evidence}


def activation_changes(source: dict, dependencies: dict, previous: dict) -> tuple[dict, list[dict]]:
    """One bounded reconsideration per verified source identity, not per restart."""
    old = previous.get('runtime-source', {})
    if any(key.startswith('dependency-scan:') and value.get('status') != 'current'
           for key, value in dependencies.items()):
        source = {'status': 'unverified', 'diagnostic': 'Enrolled blocked index incomplete; source activation reconciliation remains pending',
                  'next_action': 'Restore the existing GitHub read and rescan; preserve assignments and verify all current gates before resumption.'}
    receipt = dict(source, last_verified=old.get('last_verified'))
    changes = []
    if source['status'] == 'verified':
        receipt['last_verified'] = source['identity']
        if source['identity'] != old.get('last_verified'):
            # Reuse the existing enrolled blocked index. The coordinator reads the
            # actual blocker/claim; Python neither infers source gates nor relabels.
            parents = sorted(key for key in dependencies if reference(key))
            changes = [{'parent': key, 'status': 'source_activation_reconciliation'} for key in parents[:39]]
            if len(parents) > 39:
                changes.append({'status': 'source_activation_scope_capped',
                                'omitted_candidates': len(parents) - 39,
                                'repositories': sorted({reference(key)[0] for key in parents})[:20],
                                'diagnostics': ['reread_source_gated_blocked_assignments_in_scope']})
    return receipt, changes


def retirement_changes(repositories: list[str], previous: dict) -> tuple[dict, list[dict], int]:
    """Wake for explicit closeout handoffs only. Never inspect or remove local source."""
    current, changes = {}, []
    try:
        for repo in repositories:
            candidates = github("issue", "list", "--repo", repo, "--state", "all",
                                "--search", '"Graph retirement pending" in:comments', "--limit", "1000",
                                "--json", "number,state,stateReason,comments,closedByPullRequestsReferences")
            for issue in candidates:
                handoff = None
                for comment in issue.get("comments", []):
                    body = comment.get("body", "")
                    if body.startswith("Graph retirement pending"):
                        handoff = body
                    elif body.startswith("Graph retirement complete"):
                        handoff = None
                if handoff is None:
                    continue
                # Only explicit PR links on this handoff or GitHub's closing links.
                refs = set(PR_REF.findall(handoff))
                for pr in issue.get("closedByPullRequestsReferences", []):
                    refs.update(PR_REF.findall(pr.get("url", "")))
                evidence = []
                for pr_repo, number in sorted(refs):
                    if pr_repo.lower() != repo.lower():
                        continue  # Cross-repo text is never cleanup authority.
                    pr = github("pr", "view", number, "--repo", repo, "--json", "state,mergedAt")
                    evidence.append({"pr": f"{repo}#{number}", "state": pr["state"],
                                     "mergedAt": pr.get("mergedAt")})
                key = f"retirement:{repo.lower()}#{issue['number']}"
                current[key] = {"issue": f"{repo}#{issue['number']}", "state": issue["state"],
                                "reason": issue.get("stateReason"), "prs": evidence}
                terminal = issue["state"] == "CLOSED" or any(
                    pr["mergedAt"] or pr["state"] == "CLOSED" for pr in evidence)
                if terminal and current[key] != previous.get(key):
                    changes.append(current[key])
        return current, changes, 0
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as error:
        print(f"Retirement check failed: {error}", file=sys.stderr, flush=True)
        return {k: v for k, v in previous.items() if k.startswith("retirement:")}, [], 1


def save_observations(observations: dict) -> None:
    # Wake receipts only, never a worktree inventory. GitHub/session context owns closeout.
    path = STATE / "dependency-wakes.json"
    tmp = path.with_suffix(".tmp")
    platform.file_target(tmp)
    tmp.write_text(json.dumps(observations, sort_keys=True), encoding="utf-8")
    platform.file_permissions(tmp)
    os.replace(tmp, path)


RUN_FIELDS = '''number state stateReason body
 labels(first:100){totalCount pageInfo{hasNextPage endCursor} nodes{name}}
 comments(last:20){totalCount pageInfo{hasNextPage hasPreviousPage endCursor} nodes{body url createdAt}}
 blockedBy(first:100){totalCount pageInfo{hasNextPage endCursor} nodes{url}}
 closedByPullRequestsReferences(first:20){totalCount pageInfo{hasNextPage endCursor} nodes{url}}
 timelineItems(last:30,itemTypes:[LABELED_EVENT,UNLABELED_EVENT]){nodes{
 __typename ... on LabeledEvent{id createdAt label{name}} ... on UnlabeledEvent{id createdAt label{name}}
 } pageInfo{hasNextPage hasPreviousPage} totalCount}'''
RUN_STATE = 'run-disposition.json'


def issue_key(issue):
    return f"{issue['repo'].lower()}#{issue['number']}"


def retirement_ready_chronology(raw):
    """Corroborate a missing baseline; bounded/incomplete history cannot clear it."""
    comments, all_comments = connection(raw.get('comments'))
    events, all_events = connection(raw.get('timelineItems'))
    if not all_comments or raw['comments']['pageInfo'].get('hasPreviousPage') is not False:
        return 'incomplete_comments'
    if not all_events or raw['timelineItems']['pageInfo'].get('hasPreviousPage') is not False:
        return 'incomplete_label_history'
    from datetime import datetime, timezone

    def timestamp(row):
        value = row.get('createdAt')
        if not isinstance(value, str):
            raise ValueError('Missing timestamp')
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('Missing timezone')
        return stamp.astimezone(timezone.utc)

    try:
        if any(not isinstance(c, dict) or not all(isinstance(c.get(k), str) for k in ('body', 'url', 'createdAt')) for c in comments):
            return 'malformed_comments'
        if any(not isinstance(e, dict) or e.get('__typename') not in {'LabeledEvent', 'UnlabeledEvent'}
               or not isinstance(e.get('id'), str) or not e['id']
               or not isinstance(e.get('label'), dict) or not isinstance(e['label'].get('name'), str) for e in events):
            return 'malformed_label_history'
        comment_times = [timestamp(c) for c in comments]
        event_times = [timestamp(e) for e in events]
        if comment_times != sorted(comment_times) or event_times != sorted(event_times):
            return 'unordered_chronology'
    except (ValueError, TypeError, OverflowError):
        return 'malformed_chronology'
    handoffs = [(c, at) for c, at in zip(comments, comment_times)
                if c['body'].startswith(('Graph retirement pending', 'Graph retirement complete'))]
    ready = [(e, at) for e, at in zip(events, event_times) if e['label']['name'] == 'status:ready']
    if not handoffs or not handoffs[-1][0]['body'].startswith('Graph retirement pending'):
        return 'missing_pending_handoff'
    if not ready or ready[-1][0]['__typename'] != 'LabeledEvent':
        return 'missing_ready_event'
    return 'verified' if ready[-1][1] > handoffs[-1][1] else 'ready_not_after_handoff'


def source_disposition(raw):
    """Observe lifecycle facts, never product correctness or worker liveness."""
    unknown = {'disposition': 'unknown', 'ready_epoch': None, 'labels': [], 'related': [], 'claim_fingerprint': None}
    if not isinstance(raw, dict) or raw.get('state') not in {'OPEN', 'CLOSED'}:
        return unknown
    labels, all_labels = connection(raw.get('labels'))
    if not all_labels or any(not isinstance(v, dict) or not isinstance(v.get('name'), str) for v in labels):
        return unknown
    names = sorted(v['name'] for v in labels)
    events, _ = connection(raw.get('timelineItems'))
    ready = [e for e in events if isinstance(e, dict) and e.get('__typename') == 'LabeledEvent' and isinstance(e.get('label'), dict) and e['label'].get('name') == 'status:ready' and isinstance(e.get('id'), str)]
    epoch = ready[-1]['id'] if ready else None
    comments, all_comments = connection(raw.get('comments'))
    all_comments = all_comments and all(isinstance(c,dict) and all(isinstance(c.get(k),str)for k in ('body','url','createdAt'))for c in comments)
    claims = [c for c in comments if isinstance(c, dict) and isinstance(c.get('body'), str) and c['body'].startswith('Graph claimed —') and isinstance(c.get('url'), str) and isinstance(c.get('createdAt'),str)]
    claim = claims[-1] if claims else None
    claim_hash = hashlib.sha256(json.dumps({'body': claim['body'], 'url': claim['url']}, sort_keys=True).encode()).hexdigest() if claim else None
    declaration = dependency_declaration(raw.get('body'))
    native, native_refs = native_dependencies(raw, raw.get('_native_supported',True))
    related = declaration['refs'] if declaration['mode'] in {'references','none'} else legacy_links(raw, 'Blocked by')[0]
    # Native edges are ownership context even when current intent disagrees; never delete them.
    related = set(related or []) | native_refs
    value = {'disposition': 'unknown', 'ready_epoch': epoch, 'labels': names, 'related': ref_names(related)[:100], 'claim_fingerprint': claim_hash, '_claims': claims}
    intended = declaration['refs'] if declaration['mode'] in {'references','none'} else legacy_links(raw,'Blocked by')[0]
    value['handoff_links'] = ref_names(intended or set()) if declaration['mode'] not in {'invalid','unknown'} and native['read_status']=='complete' and not (native_refs-set(intended or [])) else []
    lifecycle = set(names) & {'status:ready','status:in-progress','status:awaiting-merge','status:blocked'}
    marker = next((c['body'].splitlines()[0] for c in reversed(comments) if isinstance(c,dict) and isinstance(c.get('body'),str) and c['body'].startswith(('Graph retirement pending','Graph retirement complete'))), None)
    value['ready_recovery_chronology'] = retirement_ready_chronology(raw)
    value['retirement'] = 'complete' if marker and marker.startswith('Graph retirement complete') else 'pending' if marker else 'unknown'
    if raw['state'] == 'CLOSED' and 'stateReason' in raw and raw.get('stateReason') in {None,'COMPLETED','NOT_PLANNED','REOPENED','DUPLICATE'}:
        value['disposition'] = 'closed'
    elif len(lifecycle) > 1:
        value['disposition'] = 'uncertain_claim_or_partial_labels'
    elif lifecycle == {'status:in-progress'}:
        worker = claim and re.search(r'\bworker(?:/session owner)?\s*:?\s+(/[A-Za-z0-9_/-]+)', claim['body'], re.I)
        value['disposition'] = 'claimed' if worker else 'uncertain_claim'
    elif lifecycle == {'status:awaiting-merge'}:
        prs, complete = connection(raw.get('closedByPullRequestsReferences'))
        valid=prs and all(isinstance(p,dict) and isinstance(p.get('url'),str) and PR_REF.fullmatch(p['url'])for p in prs)
        value['disposition'] = 'awaiting_merge' if complete and valid else 'unknown_awaiting_merge'
    elif lifecycle == {'status:blocked'}:
        notes = [c.get('body','') for c in comments if isinstance(c,dict) and isinstance(c.get('body'),str) and c['body'].startswith('Graph blocker —')]
        concrete = any(all(re.search(r'^'+field+r':\s*\S', body, re.M) for field in ('Owner','Current blocker','Next action','Clears when','Auto-resume')) for body in notes)
        valid_edges = declaration['mode'] not in {'invalid','unknown'} and native['read_status'] in {'complete','unsupported'} and bool(related)
        value['disposition'] = 'blocked' if concrete or valid_edges else 'unknown_blocked'
    elif lifecycle == {'status:ready'}:
        recent_claim = claim and (not ready or not isinstance(ready[-1].get('createdAt'),str) or claim['createdAt'] >= ready[-1]['createdAt'])
        value['disposition'] = 'uncertain_claim' if recent_claim else 'ready'
        if not all_comments and not claim:
            value['disposition'] = 'unknown_ready_ownership'
    elif 'status:ready' not in names:
        value['disposition'] = 'removed_from_eligible_scope'
    return value


def read_dispositions(refs):
    """One bounded post-run source check, at most32 exact issues per repository."""
    result, grouped = {}, {}
    for key in refs:
        item = reference(key)
        if item:
            grouped.setdefault(item[0], set()).add(item[1])
    for repo, numbers in grouped.items():
        ordered = sorted(numbers)
        for n in ordered[32:]:
            result[f'{repo}#{n}'] = {'disposition':'unknown_read_cap','ready_epoch':None,'labels':[],'related':[],'claim_fingerprint':None}
        owner, name = repo.split('/')
        aliases = ' '.join(f'i{n}:issue(number:{n}){{{RUN_FIELDS}}}' for n in ordered[:32])
        query = 'query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'+aliases+'}}'
        try:
            supported=True
            try:
                data = dependency_query(query, native=True, owner=owner, name=name)
            except NativeDependencyUnsupported:
                supported=False
                query=query.replace('blockedBy(first:100){totalCount pageInfo{hasNextPage endCursor} nodes{url}}','')
                data=dependency_query(query,owner=owner,name=name)
            repository = data.get('repository')
            if not isinstance(repository, dict):
                raise ValueError('Missing post-run repository')
            for n in ordered[:32]:
                raw = repository.get(f'i{n}')
                if isinstance(raw,dict):raw=dict(raw,_native_supported=supported)
                result[f'{repo}#{n}'] = source_disposition(raw if isinstance(raw,dict) and raw.get('number')==n else None)
        except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, AttributeError):
            for n in ordered[:32]:
                result[f'{repo}#{n}'] = {'disposition':'unknown_read','ready_epoch':None,'labels':[],'related':[],'claim_fingerprint':None}
    return result


def load_run_state():
    try:
        if platform.platform_name() == 'windows' and (STATE / RUN_STATE).exists():
            platform.check_private(STATE / RUN_STATE)
        with (STATE / RUN_STATE).open('rb')as source:raw=source.read(2*1024*1024+1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError('Disposition state cap')
        state = json.loads(raw)
        if not isinstance(state,dict) or state.get('version') != 1 or not {'version','issues','pending','hold'} <= set(state) or not isinstance(state.get('issues'),dict):
            raise ValueError('Invalid disposition state')
        if state['pending'] is not None and (not isinstance(state['pending'],dict) or not isinstance(state['pending'].get('issues'),list) or not isinstance(state['pending'].get('repositories'),list)):
            raise ValueError('Invalid pending source scope')
        if state['hold'] is not None and (not isinstance(state['hold'],dict) or not isinstance(state['hold'].get('reason'),str) or not isinstance(state['hold'].get('next_action'),str)):
            raise ValueError('Invalid ownership hold')
        for key,record in state['issues'].items():
            if not reference(key) or not isinstance(record,dict) or not isinstance(record.get('observation'),dict) or not isinstance(record['observation'].get('disposition'),str) or not isinstance(record.get('next_action'),str) or not isinstance(record.get('last_checked'),str):
                raise ValueError('Invalid scoped source record')
        return state
    except FileNotFoundError:
        return {'version':1,'issues':{},'pending':None,'hold':None}
    except (OSError, ValueError, RuntimeError):
        return {'version':1,'issues':{},'pending':None,'hold':{'reason':'unreadable_prior_effects','next_action':'Graph must inspect prior native session and actual GitHub effects before repairing the local diagnostic; do not blindly reset/replay.'},'unreadable':True}


def save_run_state(state):
    if state.get('unreadable'):
        return
    encoded = json.dumps(state,sort_keys=True)
    if len(encoded)>2*1024*1024:
        raise RuntimeError('Run disposition diagnostics exceed bounded storage; preserve prior effects and inspect Graph status')
    path = STATE / RUN_STATE
    tmp = path.with_suffix('.tmp')
    platform.file_target(tmp)
    with tmp.open('w') as output:
        platform.file_permissions(tmp)
        output.write(encoded)
    os.replace(tmp,path)


def native_session():
    try:
        if platform.platform_name() == 'windows':
            platform.check_private(STATE / 'coordinator.jsonl')
        with (STATE/'coordinator.jsonl').open() as source:
            for line in source.read(65536).splitlines():
                try:row=json.loads(line)
                except ValueError:continue
                value=row.get('thread_id') if isinstance(row,dict) and row.get('type')=='thread.started' else None
                if isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_-]{8,128}',value):return value
    except (OSError,ValueError,AttributeError,RuntimeError):
        return None


def journal_checkpoint():
    journal = platform.native_journal(ROOT, STATE)
    try:
        info=journal.stat()
        return {'inode':info.st_ino,'offset':info.st_size}
    except FileNotFoundError:
        return {'inode':None,'offset':0}
    except OSError:
        if platform.platform_name() == 'windows':
            raise  # Denied history is not an empty pre-launch checkpoint.
        return {'inode':None,'offset':0}


def ownership_hold(session, previous=None, repositories=None, checkpoint=None):
    """Existing native hooks supply possible active ownership, never task success."""
    if not session:
        return previous
    active=set((previous or {}).get('agents',[]))
    cursor=(previous or {}).get('journal_cursor') or checkpoint or {'inode':None,'offset':0}
    incomplete=False
    lost=(previous or {}).get('history_lost',False)
    try:
        journal_path = platform.native_journal(ROOT, STATE)
        if platform.platform_name() == 'windows':
            platform.check_private(journal_path.parent, directory=True)
            platform.check_private(journal_path)
        with journal_path.open('rb') as journal:
            info=os.fstat(journal.fileno());size=info.st_size
            if cursor.get('inode') not in (None,info.st_ino) or size<cursor.get('offset',0):
                lost=True;cursor={'inode':info.st_ino,'offset':0}
            journal.seek(cursor.get('offset',0))
            data=journal.read(256*1024)
            # Do not consume a partial final event; reread it after append.
            if data and not data.endswith(b'\n'):
                end=data.rfind(b'\n');data=data[:end+1]if end>=0 else b''
            cursor={'inode':info.st_ino,'offset':cursor.get('offset',0)+len(data)}
            incomplete=cursor['offset']<size
            for line in data.splitlines():
                try:row=json.loads(line)
                except (ValueError,UnicodeError):lost=True;continue
                if not isinstance(row,dict):lost=True;continue
                agent=row.get('agent_id')
                if row.get('event')in {'subagent_started','subagent_stopped'} and (not isinstance(row.get('session_id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,128}',row['session_id'])):lost=True;continue
                if row.get('session_id')!=session:continue
                if row.get('event') in {'subagent_started','subagent_stopped'} and (not isinstance(agent,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,128}',agent)):
                    lost=True;continue
                if row.get('event')=='subagent_started':active.add(agent)
                elif row.get('event')=='subagent_stopped':active.discard(agent)
    except (OSError, ValueError, RuntimeError):
        incomplete=platform.platform_name() == 'windows' or bool(active or cursor.get('inode'))
    # Reuse the existing native worker-link receipt contract. A fresh exact
    # claim match scopes ownership; it does not assert the worker is alive/done.
    receipts={}
    directory=STATE/'worker-links'
    try:
        meta=directory.lstat()
        if not stat.S_ISDIR(meta.st_mode) or directory.is_symlink():
            raise ValueError('Untrusted worker-link directory')
        if platform.platform_name() == 'windows':
            platform.check_private(directory, directory=True)
        elif meta.st_uid != os.getuid() or meta.st_mode & 0o077:
            raise ValueError('Untrusted worker-link directory')
        for path in sorted(directory.glob('*.json'))[:32]:
            try:
                with platform.private_read(path, 16384) as file:receipt=json.load(file)
                agent=receipt.get('threadId')
                if set(receipt)=={'version','repository','number','threadId','claim'} and receipt.get('version')==1 and agent in active and isinstance(receipt.get('repository'),str) and REPO.fullmatch(receipt['repository']) and receipt['repository'].lower() in {r.lower()for r in repositories or []} and type(receipt.get('number'))is int and receipt['number']>0:
                    receipts[agent]=receipt
            except (OSError,ValueError,TypeError,AttributeError,RuntimeError):pass
    except (OSError,ValueError,RuntimeError):pass
    if receipts:
        snapshots=read_dispositions([f"{r['repository'].lower()}#{r['number']}"for r in receipts.values()])
        for agent,receipt in receipts.items():
            value=snapshots.get(f"{receipt['repository'].lower()}#{receipt['number']}",{})
            claims=value.get('_claims',[])
            current={'body':claims[-1]['body'],'url':claims[-1]['url']}if claims else None
            if set(value.get('labels',[])) & {'status:ready','status:blocked','status:awaiting-merge'}:continue
            if 'status:in-progress'in value.get('labels',[]) and receipt.get('claim')==current:
                active.discard(agent)
    return {'reason':'native_worker_history_incomplete'if incomplete or lost else'unmapped_native_worker_ownership','session':session,'agents':sorted(active),'journal_cursor':cursor,'history_lost':lost,
            'next_action':'Graph must reconcile/resume the existing native session and worker claims; preserve workers. Complete hook reads plus matching stop/verified claim scope can resolve this ownership hold, not product correctness. If history was lost, verify actual native ownership/effects before repairing the local diagnostic.'} if active or incomplete or lost else None


def local_ownership_hold():
    # Reuse shared journal semantics; no receipt/GitHub queries during CLI control.
    state = load_run_state()
    if state.get('pending'):
        return 'Prior coordinator effects await shared-engine reconciliation'
    if state.get('hold') and not state['hold'].get('session'):
        return state['hold']['reason']  # A readable newer journal is not reconciliation of an unknown prior launch.
    log = STATE / 'coordinator.jsonl'
    try:
        journal = platform.native_journal(ROOT, STATE)
        if not log.exists() and not log.is_symlink():
            if state.get('last_run') or journal.exists() or journal.is_symlink():
                return 'Prior native ownership evidence missing; preserve installation'
            return state.get('hold', {}).get('reason') if state.get('hold') else None
        platform.check_private(log)
        with log.open('rb') as file:
            file.read(1)  # A directory/denied read must never become worker absence.
        session = native_session()
        if not session:
            return 'Prior native session identity unavailable; preserve installation'
        platform.check_private(journal)
        with journal.open('rb') as file:
            file.read(1)
    except (OSError, RuntimeError, subprocess.SubprocessError):
        return 'Prior native journal/log unreadable; worker ownership unknown'
    hold = ownership_hold(session, state.get('hold'), repositories=[])
    return hold.get('reason') if hold else None


def clean_source(value):
    return {k:v for k,v in value.items() if not k.startswith('_')}


def unresolved_record(key, observed, pending, parent=None):
    return {'issue':key,'observation':clean_source(observed),'ready_epoch':observed.get('ready_epoch') or pending.get('before',{}).get(key,{}).get('ready_epoch'),
            'quarantined':True,
            'last_checked':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exit_status':pending.get('exit_status'),
            'coordinator_session':native_session(),'parent_scope':parent,
            'next_action':'Graph: reread actual issue/claim/child effects and native ownership; resume existing work or apply the normal concrete GitHub lifecycle. A new verified ready-label epoch permits reconsideration; timestamps, comments, restart and graph start do not.'}


def reconcile_run(state, pending, repositories=None):
    refs=pending['issues']
    repositories=enrolled() if repositories is None else repositories
    scope={r.lower()for r in repositories}
    current=[key for key in refs if reference(key) and reference(key)[0]in scope]
    observed=read_dispositions(current)
    for key in set(refs)-set(current):
        observed[key]={'disposition':'removed_from_eligible_scope','ready_epoch':None,'labels':[],'related':[],'claim_fingerprint':None}
    resolved={'claimed','awaiting_merge','blocked','closed','removed_from_eligible_scope'}
    ready_scope=set(pending.get('ready_issues',refs))
    fields=('disposition','labels','claim_fingerprint','related','handoff_links')
    effects={key for key,value in observed.items() if key in ready_scope and not value['disposition'].startswith('unknown') and
             any(value.get(field)!=pending.get('before',{}).get(key,{}).get(field) for field in fields)}
    for key,value in observed.items():
        retirement_pending = key in pending.get('retirements',[]) and value.get('retirement')!='complete'
        if retirement_pending:
            value = dict(value,disposition='retirement_handoff_unresolved')
        if value['disposition'] in resolved:
            state['issues'].pop(key,None)
        elif effects and key in ready_scope and key not in effects and value['disposition']=='ready' and pending.get('before',{}).get(key,{}).get('disposition')=='ready' and not state['issues'].get(key,{}).get('independent_reconsideration_used'):
            # Actual effects narrow this run to another scope. Do not quarantine
            # untouched unassigned B/C merely because A partially failed.
            record=unresolved_record(key,value,pending)
            record.update(quarantined=False,independent_reconsideration_used=True,
                          next_action='Unassigned ready source had no effects while another scope changed. One normal independent consideration remains; this is not product completion or a retry timer.')
            state['issues'][key]=record
        else:
            state['issues'][key]=unresolved_record(key,value,pending)
    # A linked new ready child is not completion of an unresolved parent transition.
    related={ref:key for key,value in observed.items() if value['disposition'] not in resolved for ref in value.get('related',[]) if ref not in observed and reference(ref) and reference(ref)[0] in scope}
    if related:
        for key,value in read_dispositions(list(related)[:32]).items():
            if value['disposition']=='ready':state['issues'][key]=unresolved_record(key,value,pending,related[key])
    session=native_session()
    if platform.platform_name() == 'windows' and not session:
        state['hold']={'reason':'native_session_identity_unverified',
                       'next_action':'Reconcile the prior native launch/session, protected log and worker claims before repairing this hold; no verified session identity or worker absence is established.'}
    if session and session!=pending.get('prior_session'):
        state['hold']=ownership_hold(session,repositories=repositories,checkpoint=pending.get('journal_checkpoint'))
    state['last_run']={'exit_status':pending.get('exit_status'),'session':session,'observed_dispositions':{k:v['disposition']for k,v in observed.items()},'product_correctness':'not_judged', 'launch_error':pending.get('launch_error')}
    if pending.get('source_activation'):
        state['source_activation'] = pending['source_activation']
    state['pending']=None
    save_run_state(state)
    print('Post-run source disposition: '+json.dumps(state['last_run'],sort_keys=True),flush=True)


def refresh_run_state(state, repos):
    recovery=False
    if state.get('pending'):
        reconcile_run(state,state['pending'],repos)
    hold=state.get('hold')
    if hold and hold.get('session'):
        state['hold']=ownership_hold(hold['session'],hold,repos)
        recovery=state['hold'] is None
    for key in list(state['issues']):
        if reference(key)[0] not in {r.lower()for r in repos}:state['issues'].pop(key,None)
    keys=list(state['issues'])
    if keys:
        observed=read_dispositions(keys)
        for key,value in observed.items():
            old=state['issues'][key]
            old['last_checked']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
            if reference(key)[0] not in {r.lower()for r in repos}:
                state['issues'].pop(key,None);continue
            disposition=value['disposition']
            if disposition!='ready' and not old.get('quarantined',True):
                old['quarantined']=True
                old['next_action']=unresolved_record(key,value,{'exit_status':old.get('exit_status')})['next_action']
            old_kind=old['observation']['disposition']
            parent=observed.get(old.get('parent_scope'),{})
            if disposition=='ready' and parent.get('disposition')=='blocked' and key in parent.get('handoff_links',[]):
                state['issues'].pop(key,None);recovery=True
            elif (disposition=='ready' and value.get('ready_epoch')
                  and ((old.get('ready_epoch') is not None and value['ready_epoch']!=old['ready_epoch'])
                       or (old.get('ready_epoch') is None and old_kind=='retirement_handoff_unresolved'
                           and value.get('ready_recovery_chronology')=='verified'))
                  and not state.get('hold')
                  and not (old.get('parent_scope') and old['parent_scope'] in state['issues'])):
                # A fresh ready transition requests native reconciliation of the
                # existing claim/source, even while retirement remains pending.
                # It neither disposes source nor proves an old worker has exited.
                state['issues'].pop(key,None);recovery=True
            elif old_kind=='retirement_handoff_unresolved' and value.get('retirement')!='complete':
                value['disposition']='retirement_handoff_unresolved'
                old['observation']=clean_source(value)
                if old.get('ready_epoch') is None:
                    old['next_action'] = ('Graph: reconcile the existing claim/source and native ownership; '
                        'missing ready baseline requires complete comments and label history proving a ready event '
                        'strictly after the latest pending retirement handoff. Chronology: '
                        + value.get('ready_recovery_chronology', 'unavailable')
                        + '. Preserve source and unresolved effects; a wake does not prove worker exit or source retirement.')
            elif old.get('parent_scope') and old['parent_scope'] in state['issues']:
                old['observation']=clean_source(value)
            elif disposition in {'claimed','awaiting_merge','blocked','closed','removed_from_eligible_scope'}:
                state['issues'].pop(key,None)
            else:
                old['observation']=clean_source(value)
                old['last_checked']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
                if old.get('ready_epoch') is None and value.get('ready_epoch'):old['ready_epoch']=value['ready_epoch']
    save_run_state(state)
    return recovery


def status_line(text):
    """Plain, width-bounded terminal text; captured protocol never uses this."""
    import shutil
    import textwrap
    width = max(24, min(80, shutil.get_terminal_size().columns))
    print(textwrap.fill(text, width=width, subsequent_indent='  ', break_on_hyphens=False))


def active_work_status(state):
    """Cached lifecycle facts only; receipts/history cannot prove live workers."""
    observations = {key: record['observation'] for key, record in state['issues'].items()}
    for key, value in (state.get('pending') or {}).get('before', {}).items():
        if reference(key) and isinstance(value, dict):
            observations.setdefault(key, value)
    groups = {'Awaiting merge (cached)': [], 'Blocked (cached)': [],
              'Ownership unknown (cached)': []}
    for key, value in sorted(observations.items()):
        kind = value.get('disposition')
        lifecycle = set(value.get('labels', [])) & {'status:ready', 'status:in-progress', 'status:blocked', 'status:awaiting-merge'}
        if kind == 'retirement_handoff_unresolved':
            if lifecycle == {'status:awaiting-merge'}:
                kind = 'awaiting_merge'
            elif lifecycle == {'status:blocked'}:
                kind = 'blocked'
            elif lifecycle & {'status:in-progress', 'status:awaiting-merge'}:
                kind = 'uncertain_claim_or_partial_labels'
        if kind == 'awaiting_merge':
            group = 'Awaiting merge (cached)'
        elif kind == 'blocked':
            group = 'Blocked (cached)'
        elif kind in {'claimed', 'uncertain_claim', 'uncertain_claim_or_partial_labels', 'unknown_awaiting_merge'}:
            group = 'Ownership unknown (cached)'
        else:
            continue
        groups[group].append(key.split('/', 1)[-1])
    status_line('Live worker status unavailable')
    for label, keys in groups.items():
        if keys:
            more = f' (+{len(keys)-3} more)' if len(keys) > 3 else ''
            status_line(label + ': ' + ', '.join(keys[:3]) + more)


def compact_status(state, source):
    """Compose existing local evidence without reconciling or changing it."""
    evidence = source.get('evidence', {})
    revision = evidence.get('running') or evidence.get('installed')
    status_line('Source: ' + source['status'] + (f' · rev {revision[:7]}' if revision else ''))
    hold = state.get('hold')
    if hold:
        status_line('Dispatch: HOLD — ' + hold['reason'])
        # The existing holds all protect uncertain native ownership/effects.
        # Keep their complete repair instructions in the unchanged details JSON.
        status_line('Next: ' + ({
            'native_worker_history_incomplete': 'verify native ownership and effects; preserve assignments.',
            'unmapped_native_worker_ownership': 'reconcile native session and worker claims; preserve assignments.',
            'native_session_identity_unverified': 'verify native launch/session and worker claims; preserve assignments.',
            'unreadable_prior_effects': 'inspect prior native session and issue effects; preserve assignments.',
        }.get(hold['reason']) or hold['next_action']))
    elif state.get('pending'):
        status_line('Dispatch: HOLD — previous coordinator effects await reconciliation')
        status_line('Next: reconcile previous coordinator effects; preserve assignments.')
    else:
        status_line('Dispatch: no hold recorded')
    if source['status'] != 'verified':
        status_line('Check source: graph version --json (watcher/source identity unverified)')
    if (state.get('last_run') or {}).get('launch_error'):
        status_line('Native launch unavailable: repair Codex access and reconcile assignments.')
    active_work_status(state)
    counts = Counter(record['observation']['disposition'] for record in state['issues'].values())
    held = sum(record.get('quarantined', True) for record in state['issues'].values())
    names = {'retirement_handoff_unresolved': 'handoffs', 'unknown_blocked': 'unknown blocked',
             'unknown_read_cap': 'read capped'}
    parts = [f"{count} {names.get(kind, kind.replace('_', ' '))}"
             for kind, count in counts.most_common(3)]
    if len(counts) > 3:
        parts.append(f'{sum(counts.values()) - sum(count for _, count in counts.most_common(3))} other')
    recovery = f'Recovery: {held} held'
    if len(state['issues']) != held:
        recovery += f" · {len(state['issues']) - held} independent consideration remaining"
    if parts:
        recovery += ' · ' + ' / '.join(parts)
    status_line(recovery)
    status_line('Details: graph status --details · source: graph version --json')


def status_report():
    """Versioned, allowlisted projection of local receipts; no runtime probes."""
    report = {'schema_version': 1,
              'diagnostics': {'status': 'missing', 'freshness': 'unknown',
                              'freshness_window_seconds': 300, 'fresh_records': None,
                              'stale_records': None, 'scoped_blocked_count': None},
              'last_coordinator': {'status': 'unavailable', 'exit_status': None,
                                   'freshness': 'unknown', 'product_correctness': 'unknown'},
              'queue': {'status': 'unavailable', 'candidate_count': None, 'blocked_count': None},
              'source_identity': {'status': 'unavailable', 'command': 'graph version --json'},
              'live_workers': 'unknown', 'remote_delivery': 'unknown', 'native_hooks': 'unknown',
              'limits': 'Local historical diagnostics only; scoped records are not queue totals. '
                        'File timestamps do not prove observation time, elapsed runtime or liveness.'}
    try:
        with platform.private_read(STATE / RUN_STATE, limit=2 * 1024 * 1024) as file:
            state = json.loads(file.read(2 * 1024 * 1024 + 1))
        if (not isinstance(state, dict) or type(state.get('version')) is not int
                or state['version'] != 1 or not isinstance(state.get('issues'), dict)
                or not {'pending', 'hold'} <= state.keys()):
            raise ValueError('Invalid receipt')
        fresh, stale, blocked = 0, 0, 0
        now = time.time()
        for key, record in state['issues'].items():
            if (not isinstance(key, str) or not reference(key) or not isinstance(record, dict)
                    or not isinstance(record.get('observation'), dict)
                    or not isinstance(record['observation'].get('disposition'), str)):
                raise ValueError('Invalid scoped record')
            stamp = record.get('last_checked')
            if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', stamp):
                raise ValueError('Invalid observation time')
            parsed = time.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
            if time.strftime('%Y-%m-%dT%H:%M:%SZ', parsed) != stamp:
                raise ValueError('Invalid observation time')
            age = now - calendar.timegm(parsed)
            if age < 0:
                raise ValueError('Future observation time')
            if age > 300:
                stale += 1
                continue
            fresh += 1
            blocked += record['observation']['disposition'] == 'blocked'
        report['diagnostics'].update(status='available',
            freshness=('mixed' if fresh and stale else 'stale' if stale else 'fresh' if fresh else 'unknown'),
            fresh_records=fresh, stale_records=stale,
            scoped_blocked_count=blocked if fresh else None)
        last = state.get('last_run')
        # Existing last_run receipts have no completion timestamp. Expose only
        # a valid historical exit code, never session IDs, errors or success claims.
        if isinstance(last, dict) and type(last.get('exit_status')) is int and -255 <= last['exit_status'] <= 255:
            report['last_coordinator'].update(status='last_known', exit_status=last['exit_status'])
    except FileNotFoundError:
        pass
    except (OSError, ValueError, RuntimeError, OverflowError):
        report['diagnostics'].update(status='unavailable', freshness='unknown')
    return report


def run_status(details=False, as_json=False):
    if as_json:
        print(json.dumps(status_report(), indent=2, sort_keys=True))
        return
    state=load_run_state()
    if details:
        print(json.dumps(state, indent=2, sort_keys=True))
        return
    if sys.stdout.isatty():
        compact_status(state, activation_source())
        return
    # Display current read-only evidence, not a saved activation warning from a
    # prior coordinator. Keep that receipt and every recovery gate untouched.
    source = activation_source()
    evidence = source.get('evidence', {})
    print(f"Graph current local source: {source['status']}; service={evidence.get('service', 'unknown')}; "
          f"dirty={evidence.get('dirty', 'unknown')}; runningDirty={evidence.get('runningDirty', 'unknown')}; "
          f"runtimeMatches={evidence.get('runtimeMatches', 'unknown')}")
    print('Graph revisions: '+ '; '.join(f"{label}={evidence.get(key, 'unknown')}" for label,key in
          (('installed','installed'), ('running','running'), ('origin/main','localRef'))))
    print(f"Graph remote main (cached observation, not a live read): {evidence.get('remote', 'unknown')}; "
          f"observedAt={evidence.get('remoteAt', 'unknown')}; relation={evidence.get('relation', 'unknown')}; "
          f"comparedInstalled={evidence.get('comparedInstalled', 'unknown')}")
    if evidence.get('remoteError'):
        print('Graph last remote check failed: '+evidence['remoteError'])
    if source['status'] == 'unverified':
        print('Graph source activation unverified: '+source['diagnostic'])
        print(source['next_action'])
    if state.get('last_run'):
        print('Graph last coordinator exit: '+str(state['last_run'].get('exit_status'))+'; source dispositions observed, product correctness not judged.')
        if state['last_run'].get('launch_error'):
            print('Graph native launch unavailable: inspect the installed Codex executable/session and reconcile preserved assignments after repair. A genuine source transition can retry; unrelated eligible work remains independent.')
    if state.get('hold'):
        print('Graph dispatch hold: '+state['hold']['reason'])
        print(state['hold']['next_action'])
    else:
        print('Graph dispatch hold: prior coordinator effects await reconciliation' if state.get('pending') else 'Graph dispatch hold: none recorded')
    if state.get('pending'):print('Graph: prior coordinator effects await source reconciliation; no blind replay.')
    counts = Counter(record['observation']['disposition'] for record in state['issues'].values())
    quarantined = sum(record.get('quarantined', True) for record in state['issues'].values())
    print(f"Graph scoped diagnostics: {len(state['issues'])} total; quarantined={quarantined}; "
          f"independent consideration remaining={len(state['issues'])-quarantined}; dispositions: "
          + (', '.join(f'{kind}={count}' for kind,count in sorted(counts.items())) or 'none'))
    examples = {}
    for key,record in sorted(state['issues'].items()):
        examples.setdefault((record['observation']['disposition'], record.get('quarantined', True)), (key,record))
    actions = set()
    for key,record in list(examples.values())[:3]:
        scope='scoped suppression'if record.get('quarantined',True)else'one independent consideration remains'
        print(f"Graph unresolved {key}: {record['observation']['disposition']} ({scope}; last checked {record['last_checked']}; exit {record.get('exit_status')}, not completion)")
        if record['next_action'] not in actions:
            print(record['next_action'])
            actions.add(record['next_action'])
    print(f"Graph full recovery details: {(STATE / RUN_STATE).absolute()} (all records preserved; status is read-only)")


def coordinator_prompt(repos: list[str], changes: list[dict] | None = None,
                       retirements: list[dict] | None = None, run_context: dict | None = None) -> str:
    names = "\n".join(f"- {repo}" for repo in repos)
    return (
        "You are the Graph Community engineering coordinator. Read AGENTS.md; "
        "use the effective library paths below for its linked policies before assigning work.\n\n"
        + library_instructions(ROOT, Path(os.environ.get(
            "VEZRYN_GRAPH_LIBRARY", str(CONFIG.parent / "library"))).expanduser()) + "\n"
        "Watcher scope — these are ALL currently enrolled repositories:\n"
        f"{names}\n\n"
        "Dependency reconciliation candidates (observations, not proof of delivery):\n"
        + json.dumps(changes or [], sort_keys=True) + "\n"
        "Observation modes distinguish legacy discovery, current references, explicit None, invalid and unknown. "
        "Null links and stale last-known-good are never a current empty dependency set. "
        "Inspect each referenced CURRENT parent and ALL its prerequisites with live GitHub/source evidence. "
        "A body graph-dependencies declaration overrides historical and reverse text; invalid declarations, "
        "unknown/incomplete reads and native-only discrepancies must be reconciled before requeue. "
        "Retiring an edge requires a source-grounded reason while preserving useful history. "
        "A closed child alone, not-planned closure, draft/unmerged PR or unrelated merge is not accepted delivery. "
        "Requeue only when every blocker for the next engineering step is satisfied; retain genuine founder "
        "decisions and unenrolled dependencies. Follow ISSUE_LIFECYCLE.md for one evidence comment and "
        "blocked-to-ready transition, or state the remaining blocker only if new information warrants a comment. "
        "Never dispatch these blocked candidates directly. Then select from the normal ready queue.\n\n"

        "Source activation candidates are bounded reconsideration, never proof of an unblock. "
        "Read each current blocker, existing claim/handoff and ALL current dependencies. Verify the "
        "required effective installed guidance, actual running process/revision, clean source and live "
        "cross-repository delivery/ancestry. Remote merge or restart alone is insufficient. Keep blocked "
        "on stale/draining/unknown/mismatched/diverged source, other gates, genuine founder-only action "
        "or ambiguous in-flight ownership; record one actionable diagnostic only when evidence changes. "
        "When all next-step gates are satisfied, write one concise evidence comment and clear blocked "
        "and stale reason labels. Resume a verified existing assignment/claim with its exact preserved "
        "source and one accountable owner; update its original claim rather than create a competing "
        "claim, duplicate specialist work or reset completed progress. Otherwise restore ready for "
        "normal selection. This recovery needs no founder relabeling or routine approval.\n\n"

        "Retirement reconciliation candidates (observations, never deletion authority):\n"
        + json.dumps(retirements or [], sort_keys=True) + "\n"
        "Before selection and exit, reconcile these and known worker closeouts using ISSUE_LIFECYCLE.md "
        "and the effective worktree-retirement playbook. Read original claims/handoffs and live PR/issue "
        "outcomes; prove exact repository/branch/worktree ownership, worker/process inactivity, no dependent "
        "users, cleanliness and integration of ALL source. Preserve paused, dirty, active, shared, "
        "unmerged or uncertain work. Do not scan arbitrary old worktrees. Record one actionable reason "
        "when preservation is needed; do not repeat unchanged comments. GitHub branch deletion is not "
        "proof of safe disposal. The watcher only supplies references; native Codex owns Git actions.\n\n"

        "Post-run recovery context (source facts, not product-success judgments):\n"
        + json.dumps(run_context or {}, sort_keys=True) + "\n"
        "Respect scoped unresolved issues and preserve surviving workers. Do not blindly replay "
        "issue creation, dispatch, merges or cleanup. Reconcile actual parent/child claims and effects "
        "through existing native session/GitHub recovery before new work in those scopes. "
        "Unrelated safely independent ready candidates remain useful; no founder approval is needed "
        "for routine source investigation/recovery. A new child or delivery-note edit is not a completed "
        "planning handoff; verify actual lifecycle and next-step eligibility.\n\n"
        "Only start new assignments for open issues marked status:ready in the enrolled "
        "repositories. Never dispatch blocked, already-owned, waiting-to-merge, "
        "or wrong-repository tickets, even when they carry the ready label. "
        "You can read other GitHub issues for dependency context only. "
        "Use your native GitHub tools/gh CLI to inspect the COMPLETE issues, labels, "
        "related PRs and dependencies. YOU choose priority, model and reasoning effort, "
        "one playbook and relevant skills according to the Markdown policies. "
        "Claim each worker issue in GitHub with status:in-progress and a Pacific-time "
        "start comment as described in ISSUE_LIFECYCLE.md. Dispatch independent tasks "
        "to native Codex subagents and continue selecting work "
        "while they operate. Pass each worker the actual issue and the literal selected "
        "playbook and skill instructions. Let workers use normal Codex and GitHub tools "
        "for implementation, validation, PRs, issue comments and labels. Do not "
        "launch independent LLM reviews for routine changes. Do not build new Graph machinery.\n\n"
        "Keep track of active subagents and reconcile completion; do not exit while "
        "your own workers are still active. When no actionable tasks or workers remain, "
        "exit normally. The watcher will relaunch you after a meaningful issue change. "
        "Enrollment is a watcher-discovery filter only, not a GitHub credential or "
        "worker termination control.\n"
    )


class DispatchStopped(RuntimeError):
    pass


def launch(repos: list[str], changes: list[dict] | None = None, lock_fd: int | None = None,
           retirements: list[dict] | None = None, run_context: dict | None = None) -> int:
    platform.launch_prerequisites()
    platform.prepare_state(STATE)
    command = [platform.executable("codex"), "exec", "--json", "-C", str(ROOT), "-"]
    with platform.open_lock(STATE / 'stop-intent.lock') as intent:
        platform.lock_exclusive(intent, blocking=platform.platform_name() == 'linux')
        if STOP_REQUEST.exists():
            raise DispatchStopped('Graph stop requested before native launch')
        print("Launching native Codex coordinator", flush=True)
        with (STATE / "coordinator.jsonl").open("w", encoding="utf-8") as log:
            platform.file_permissions(STATE / "coordinator.jsonl")
            # Preserve the existing lock if the watcher exits before its coordinator.
            with platform.coordinator_launch(lock_fd) as options:
                proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                                        **options, env={**os.environ, "VEZRYN_GRAPH_ROOT": str(ROOT),
                                                        "VEZRYN_GRAPH_PYTHON": sys.executable})
    assert proc.stdin is not None
    try:
        proc.stdin.write(coordinator_prompt(repos, changes, retirements, run_context).encode("utf-8"))
    finally:
        proc.stdin.close()
    return proc.wait()


def watch(interval: int, once: bool) -> None:
    platform.require("runtime_lock")
    platform.prepare_state(STATE)
    platform.native_journal(ROOT, STATE)  # Refuse unresolved legacy Windows history before dispatch.
    with platform.open_lock(STATE / "watcher.lock") as lock:
        try:
            platform.lock_exclusive(lock)
        except BlockingIOError as error:
            raise RuntimeError("Graph watcher is already running") from error
        from graph_update import record_launch
        record_launch()
        runs = load_run_state()
        try:
            observations = json.loads((STATE / "dependency-wakes.json").read_text())
            if not isinstance(observations, dict):
                raise ValueError("Invalid dependency wake receipts")
        except (FileNotFoundError, ValueError):
            # Receipts are disposable, not authoritative dependency state.
            observations = {}
        while True:
            if STOP_REQUEST.exists():
                print("Graph stopping: no new assignments", flush=True)
                return
            repos = enrolled()  # Live reload: enrollment/revocation only controls watcher reads.
            issues, failures = backlog(repos)
            dependencies, changes, dependency_failures = dependency_changes(repos, observations)
            retirements, closeouts, retirement_failures = retirement_changes(repos, observations)
            recovery = refresh_run_state(runs, repos)
            previous_source = runs.get('source_activation') or observations.get('runtime-source', {})
            activation, source_changes = activation_changes(activation_source(), dependencies, {'runtime-source': previous_source})
            changes.extend(source_changes)
            observed = {**dependencies, **retirements, 'runtime-source': activation}
            if activation != observations.get('runtime-source') and activation['status'] == 'unverified':
                print('Source activation unverified: '+activation['diagnostic']+'; '+activation['next_action'], flush=True)
            diagnostic = dict(activation)
            if source_changes:
                # Keep the event unacknowledged through ownership holds. The
                # attempted run and its source receipt reconcile in one state save.
                diagnostic['last_verified'] = previous_source.get('last_verified')
            if runs.get('source_activation') != diagnostic:
                runs['source_activation'] = diagnostic
                save_run_state(runs)
            if dependency_failures:
                print(f'Dependency observations incomplete: {dependency_failures}; unknown/stale, never cleared', flush=True)
            if STOP_REQUEST.exists():
                print("Graph stopping: no new assignments", flush=True)
                return
            eligible = [issue for issue in issues if issue_key(issue) not in runs['issues'] or not runs['issues'][issue_key(issue)].get('quarantined',True)]
            if runs.get('hold'):
                print('Dispatch held: '+runs['hold']['reason']+'; workers preserved; use graph status',flush=True)
            elif eligible or changes or closeouts or recovery:
                # One gate with the idle updater. Never create pending effects or
                # launch after an automatic/manual stop wins this boundary.
                with platform.open_lock(STATE / 'dispatch.lock') as dispatch:
                    try:
                        platform.lock_exclusive(dispatch)
                    except BlockingIOError:
                        print('Dispatch gate busy; no coordinator launched', flush=True)
                    else:
                        if STOP_REQUEST.exists():
                            print('Graph stopping: no new assignments', flush=True)
                            return
                        refs = {issue_key(issue) for issue in eligible}
                        refs.update(change['parent'] for change in changes if isinstance(change.get('parent'),str) and reference(change['parent']))
                        refs.update(item['issue'].lower() for item in retirements.values() if reference(item.get('issue','')))
                        before = read_dispositions(refs)
                        pending = {'issues':sorted(refs), 'repositories':repos, 'prior_session':native_session(),
                                   'ready_issues':[issue_key(i)for i in eligible],
                                   'source_activation':activation if source_changes else None,
                                   'journal_checkpoint':journal_checkpoint(),
                                   'before':{k:clean_source(v) for k,v in before.items()},
                                   'retirements':[item['issue'].lower() for item in retirements.values() if reference(item.get('issue',''))],
                                   'exit_status':None}
                        runs['pending'] = pending
                        save_run_state(runs)  # Durable before launch: restart must reconcile, never blindly replay.
                        context = {'ready_candidates':[issue_key(i) for i in eligible],
                                   'scoped_unresolved':{k:{'observation':v['observation'],'next_action':v['next_action']} for k,v in runs['issues'].items() if v.get('quarantined',True)},
                                   'resume_existing_session':(runs.get('last_run') or {}).get('session'),
                                   'source_activation':activation,
                                   'source_recovery_event':recovery}
                        try:
                            pending['exit_status'] = launch(repos, changes, lock.fileno(), list(retirements.values()), context)
                        except DispatchStopped:
                            runs['pending'] = None  # No launch/log replacement occurred.
                            save_run_state(runs)
                            print('Graph stopping: no new assignments', flush=True)
                            return
                        except OSError as error:
                            pending['launch_error'] = 'native_launch_unavailable'
                            print(f'Native coordinator launch unavailable: {error}', file=sys.stderr, flush=True)
                        save_run_state(runs)
                        reconcile_run(runs, pending, enrolled())
                        # Receipt acknowledgment records a checked source/diagnostic, never semantic success.
                        observations = observed
                        save_observations(observations)
                        print(f"Coordinator exit diagnostic: {pending.get('exit_status')} (not completion)",flush=True)
            elif not issues and failures == 0:
                print('No status:ready issues in enrolled repositories',flush=True)
            elif not eligible and issues:
                print('Ready work has scoped unresolved dispositions; independent new work remains eligible; use graph status',flush=True)
            if not changes and not closeouts:
                observations = observed
                save_observations(observations)
            if once:
                return
            for _ in range(interval):
                if STOP_REQUEST.exists():
                    print("Graph stopping: no new assignments", flush=True)
                    return
                time.sleep(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities", help="Versioned OS capability JSON; no runtime ownership inference")
    sub.add_parser("doctor", help="Read-only accounts-free local preflight; no dispatch").add_argument("--json", action="store_true")
    sub.add_parser("queue", help="Read current GitHub ready-label candidates; no dispatch").add_argument("--json", action="store_true")
    status = sub.add_parser("status", help="Read local post-run disposition diagnostics; no network or inference")
    status_format = status.add_mutually_exclusive_group()
    status_format.add_argument("--details", action="store_true")
    status_format.add_argument("--json", action="store_true")
    sub.add_parser("library", help="Show effective Markdown paths and override precedence").add_argument(
        "--explain", action="store_true", help="Read-only provenance JSON; omit absolute paths and contents")
    repo_cmd = sub.add_parser("repo", help="Manage watched GitHub repositories")
    repo_sub = repo_cmd.add_subparsers(dest="action", required=True)
    for name in ("add", "revoke", "list"):
        p = repo_sub.add_parser(name)
        if name != "list":
            p.add_argument("repository")
    check = repo_sub.add_parser("check", help="Explicit authenticated read-only repository preflight; no dispatch")
    check.add_argument("repository", nargs="?", help="owner/name; omitted checks enrolled repositories only")
    check.add_argument("--json", action="store_true")
    watcher = sub.add_parser("watch", help="Watch GitHub and launch Codex when issues change")
    watcher.add_argument("--interval", type=int, default=180, help="Polling seconds (default: 180)")
    watcher.add_argument("--once", action="store_true", help="Check once, including a coordinator run if needed")
    args = parser.parse_args()
    try:
        if args.command == "capabilities":
            print(json.dumps(platform.capabilities()))
        elif args.command == "doctor":
            print_doctor(args.json)
        elif args.command == "queue":
            return print_queue(args.json)
        elif args.command == "status":
            run_status(args.details, args.json)
        elif args.command == "library":
            overrides = Path(os.environ.get(
                "VEZRYN_GRAPH_LIBRARY", str(CONFIG.parent / "library"))).expanduser()
            if args.explain:
                print(json.dumps(library_explain(ROOT, overrides), indent=2))
            else:
                print(library_instructions(ROOT, overrides))
        elif args.command == "repo":
            if args.action == "check":
                return print_repo_check(args.repository, args.json)
            manage(args.action, getattr(args, "repository", None))
        else:
            if args.interval < 1:
                parser.error("--interval must be positive")
            watch(args.interval, args.once)
    except (ValueError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Watcher interrupted", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
