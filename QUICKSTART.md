# Beginner quickstart

Graph Community is public at `Vezryn-LLC/graph-community` under [Apache-2.0](LICENSE).
Start with a repository you control and no production data. Keep manifest-verified
source separate from stateful runtime trials; the local check needs no accounts.
Native Codex/GitHub installation, authentication and permissions remain yours.

## Prerequisites

Python 3.11+ and Git are required. No pip packages or bundled executables are
needed. Linux `bin/graph` additionally uses Bash, GNU readlink, systemd user
services and `/usr/bin/python3` (which must be 3.11+). Foreground Python does not
need systemd. Mac needs an arm64 native session and the user's GUI launchd domain.
Windows needs native Windows 11 x64 Python, `git.exe`, `gh.exe`, `codex.exe` on
absolute PATH entries; batch shims and WSL are not native Windows qualification.

Actual work additionally needs an authenticated GitHub CLI and a native Codex
client/account with worker delegation and trusted lifecycle hooks. Setup and
sign-in are interactive user actions. Verify the exact client version, trusted
hook loading and native event delivery before unattended work. Nothing below
signs in, authorizes a tool or grants access.

On Linux/macOS, put the native Codex executable on PATH. Recognized npm
installations resolve directly to their native payload so Node cannot discard
the inherited watcher lock. Unknown script wrappers or missing/nonexecutable
native payloads are rejected; Graph does not fall back to an unqualified wrapper.

## Acquire source and make a fresh runtime copy

Choose one path below. As observed on 2026-11-12, the published release is
**v0.1.1**. It has `ci/check.py`, `capabilities` and `smoke.py`, but **no doctor,
queue or first-issue fixture**. The pinned current-source route includes those
newer features; they are **unreleased**, not additions to v0.1.1.

These commands need Python 3.11+, internet access and (for source) Git, but no
GitHub sign-in, Codex account or running Graph process. Run them in a **new empty
directory outside any existing checkout/runtime**. Do not copy an installation
that has already been used. If a command fails, stop before the next command.

### Published v0.1.1

On Linux/macOS, open a terminal in your chosen parent directory:

```sh
mkdir graph-local-release
cd graph-local-release
python3 -c "from urllib.request import urlretrieve; base='https://github.com/Vezryn-LLC/graph-community/releases/download/v0.1.1/'; [urlretrieve(base+n,n) for n in ('graph-community-v0.1.1.tar.gz','SHA256SUMS','MANIFEST.json')]"
python3 -c "from pathlib import Path; import hashlib; sums=Path('SHA256SUMS').read_bytes(); assert hashlib.sha256(sums).hexdigest() == '845dd4d7f8ec98c6aa8442c97b8058a988d6a314d8b797148ec1371b27ba6348'; expected=dict(line.split()[::-1] for line in sums.decode().splitlines()); assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==expected[n] for n in ('graph-community-v0.1.1.tar.gz','MANIFEST.json')); print('Release checksums match')"
python3 -c "import shutil; shutil.unpack_archive('graph-community-v0.1.1.tar.gz','source')"
python3 -c "from pathlib import Path; assert Path('source/graph-community-v0.1.1/MANIFEST.json').read_bytes()==Path('MANIFEST.json').read_bytes(); print('Embedded manifest matches')"
python3 -c "import shutil; shutil.copytree('source/graph-community-v0.1.1','runtime')"
cd runtime
python3 -B ci/check.py
python3 -B watcher.py capabilities
python3 -B smoke.py
```

On native Windows PowerShell, from your chosen parent directory:

```powershell
New-Item -ItemType Directory graph-local-release -ErrorAction Stop
Set-Location graph-local-release
$Python = (Get-Command python.exe).Source
& $Python -c "from urllib.request import urlretrieve; base='https://github.com/Vezryn-LLC/graph-community/releases/download/v0.1.1/'; [urlretrieve(base+n,n) for n in ('graph-community-v0.1.1.tar.gz','SHA256SUMS','MANIFEST.json')]"
& $Python -c "from pathlib import Path; import hashlib; sums=Path('SHA256SUMS').read_bytes(); assert hashlib.sha256(sums).hexdigest() == '845dd4d7f8ec98c6aa8442c97b8058a988d6a314d8b797148ec1371b27ba6348'; expected=dict(line.split()[::-1] for line in sums.decode().splitlines()); assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==expected[n] for n in ('graph-community-v0.1.1.tar.gz','MANIFEST.json')); print('Release checksums match')"
& $Python -c "import shutil; shutil.unpack_archive('graph-community-v0.1.1.tar.gz','source')"
& $Python -c "from pathlib import Path; assert Path('source/graph-community-v0.1.1/MANIFEST.json').read_bytes()==Path('MANIFEST.json').read_bytes(); print('Embedded manifest matches')"
& $Python -c "import shutil; shutil.copytree('source/graph-community-v0.1.1','runtime')"
Set-Location runtime
& $Python -B .\ci\check.py
& $Python -B .\watcher.py capabilities
& $Python -B .\smoke.py
```

Expected: `Release checksums match`, `Embedded manifest matches`, then a package
check ending in `"local_check": "PASS"` and passing primitive smoke. The archive
SHA-256 is `9611439143d5eaf9840b29b8a7ce8ddd42643b50a3a215c5ba5e3a8558646dda`.
The checksum-list digest above pins the published list rather than trusting a
freshly downloaded list alone. The separate manifest is compared to the embedded
one; `ci/check.py` checks the payload against it.

Continue only with the **[v0.1.1 tagged Quickstart](https://github.com/Vezryn-LLC/graph-community/blob/v0.1.1/QUICKSTART.md)**
and its [tagged platform limits](https://github.com/Vezryn-LLC/graph-community/blob/v0.1.1/PLATFORMS.md).
You have already completed that guide's local check. Stop here for an accounts-free
release trial; do not run the newer commands or exercise below against v0.1.1.

### Pinned current source (unreleased)

The observed public `main` revision is
[`594629f7e8860e1fdc40e934b31ac7dd82d873ac`](https://github.com/Vezryn-LLC/graph-community/tree/594629f7e8860e1fdc40e934b31ac7dd82d873ac).
Use that exact commit for this trial, rather than assuming today's moving `main`
is identical. This route consumes Git's ordinary tracked-file archive; it does
not modify or replace any published release or producer archive.

Linux/macOS, from your chosen parent directory:

```sh
mkdir graph-local-source
cd graph-local-source
git clone https://github.com/Vezryn-LLC/graph-community.git source
git -C source checkout --detach 594629f7e8860e1fdc40e934b31ac7dd82d873ac
git -C source rev-parse HEAD
git -C source archive --format=tar --output=../payload.tar HEAD
python3 -c "import shutil; shutil.unpack_archive('payload.tar','runtime')"
cd runtime
```

Native Windows PowerShell, from your chosen parent directory:

```powershell
New-Item -ItemType Directory graph-local-source -ErrorAction Stop
Set-Location graph-local-source
$Python = (Get-Command python.exe).Source
git clone https://github.com/Vezryn-LLC/graph-community.git source
git -C source checkout --detach 594629f7e8860e1fdc40e934b31ac7dd82d873ac
git -C source rev-parse HEAD
git -C source archive --format=tar --output=../payload.tar HEAD
& $Python -c "import shutil; shutil.unpack_archive('payload.tar','runtime')"
Set-Location runtime
```

Confirm the printed HEAD is the exact pinned commit. Git archive includes tracked
dotfiles such as `.codex/hooks.json` and executable file modes, excludes `.git`
and untracked/ignored runtime state, and does not follow another checkout's Git
store. The release archive likewise contains only its published payload.
`shutil.copytree` includes dotfiles and uses `copy2` to preserve payload modes on
POSIX; Windows does not provide equivalent POSIX mode evidence. Keep `source`
pristine and run only from the fresh sibling `runtime`, never overlaying an old
runtime. Later profiles, journals and enrollment belong outside pristine source.

Hashes and the Git commit identify expected bytes and detect mismatch. They are
**integrity evidence, not publisher signatures**: trust in the repository, HTTPS
origin and the source of these expected digests is still required. Neither the
manifest nor a clean check proves authenticity, account rights or native hooks.
Do not execute an unexpected download just because its own manifest agrees.

Continue with the local check below and the existing first-issue walkthrough.
For later revisions, use the guide shipped with that revision and recheck its
capabilities; this pinned trial does not claim to follow future `main` changes.

## Local check, without accounts or services

For the pinned unreleased source above, you are now in `graph-local-source/runtime`.
On Linux or Mac:

```sh
python3 --version
python3 -B ci/check.py
python3 -B watcher.py doctor
python3 -B watcher.py capabilities
python3 -B smoke.py
```

On native Windows PowerShell:

```powershell
$Python = (Get-Command python.exe).Source
& $Python --version
& $Python -B .\ci\check.py
& $Python -B .\watcher.py doctor
& $Python -B .\watcher.py capabilities
& $Python -B .\smoke.py
```

`ci/check.py` checks manifest bytes/completeness, compiles Python in memory, imports
entrypoints and executes the local primitive smoke in fresh temporary state. It
uses no GitHub/Codex credentials, enrollment, service manager or model call.
A passing smoke proves only the operations named in its output. The acquisition,
copy and local checks here were exercised on Linux x86_64 with Python 3.14.7.
The macOS and PowerShell forms have not been run on native hosts for this
documentation change; existing native-platform limits in [PLATFORMS.md](PLATFORMS.md)
remain in force.

For a tiny executable task before any account setup, try the
[local first-issue example](examples/first-issue/README.md). Its baseline passes
and one named acceptance test deliberately fails until you add `--uppercase`.
The example needs no Graph dispatch; it also explains the optional real PR journey.

`watcher.py doctor` is a read-only, accounts-free local preflight (`--json` for
structured facts). It discovers tools without running them, checks native Codex
launcher resolution, safely counts configured repositories without listing them,
and reports effective guidance availability and existing platform limits. Unsafe,
unreadable or invalid config is reported as unknown; absent config is left absent.
It creates no state and makes no network, authentication, service or worker call.
It reports diagnostics and exits normally even when prerequisites are missing;
neither its exit status nor tool presence proves authentication, trusted hooks,
permissions or native-host qualification. `watch --once` below is real dispatch.

The platform entrypoints forward the same read-only diagnostics and preserve the
watcher's stdout and exit status. Use these commands from the runtime copy:

| Platform | Local facts | Effective library provenance | Current GitHub candidates |
| --- | --- | --- | --- |
| Linux | `bin/graph doctor --json` | `bin/graph library --explain` | `bin/graph queue --json` |
| macOS | `python3 -B graph_macos.py doctor --json` | `python3 -B graph_macos.py library --explain` | `python3 -B graph_macos.py queue --json` |
| Windows PowerShell | `& $Python -B .\graph_windows.py doctor --json` | `& $Python -B .\graph_windows.py library --explain` | `& $Python -B .\graph_windows.py queue --json` |

Omit `--json` or `--explain` for the existing human-readable output. These
commands need no service installation or service-manager probe. Only `queue`
reads GitHub; it requires the account access described below. The macOS and
Windows runners retain their experimental native-platform qualification limits;
platform-isolated routing tests do not establish native service qualification.

## Look at current candidates without dispatch

After enrolling repositories, use `python3 -B watcher.py queue` (or `queue --json`)
to read their current open `status:ready` metadata through your authenticated
GitHub CLI, using the platform entrypoints above or the watcher directly. This command makes no
state changes and launches no coordinator, worker, model call or service. It
reads issue numbers, update timestamps and labels, never bodies or comments.

`READY_LABEL_CANDIDATE` is not Graph-validated eligibility: ownership,
dependencies, blocked comments and recovery/source gates may exclude it. Conflicting
lifecycle labels remain visible. Each repository reports its read timestamp and
source age; a failed read or the 1000-issue cap makes the snapshot incomplete and
returns exit code 1. An empty successful read means no ready-label candidates in
that repository; a failed read does not mean an empty queue. JSON schema version 1
includes `generated_at`, `complete`, configuration status and per-repository
status, observation time, age and candidates. Raw errors, local paths and credentials
are withheld. Invalid or duplicate enrollment is reported without reading GitHub.

`queue` looks at current GitHub metadata; `status` describes prior local runs;
`watch --once` can dispatch real work. Accounts-free verification remains
`ci/check.py` with fake GitHub responses.

For local terminal/script monitors, use `python3 -B watcher.py status --json`
(or `bin/graph status --json`). Schema version 1 reports diagnostic availability
and freshness, the last known coordinator exit code, and explicit unknowns. It
reads only the local run-disposition receipt, without GitHub or runtime probes.
Scoped observations are fresh for 300 seconds from `last_checked`; stale,
future-dated or malformed values cannot supply current counts. `scoped_blocked_count`
counts only fresh blocked diagnostic records, never the repository backlog.
Queue candidate/blocked totals remain `null` because these receipts are not a
complete queue snapshot. Last-run receipts lack completion timestamps, so their
freshness stays unknown; exit code 0 does not prove delivery. Source identity is
unavailable here (use `graph version --json`), and worker liveness, native hooks
and remote delivery stay unknown. Missing/invalid receipts produce JSON with
missing/unavailable diagnostics, without raw errors or private paths. Plain
`status` and `status --details` keep their existing output; format flags are
mutually exclusive.

## One real issue, only after native-host/account authorization

Use an authorized disposable PRIVATE test repository with no production data;
reuse an existing qualification repository when appropriate rather than creating
a duplicate. Read
[AGENTS.md](AGENTS.md) and the [default library](docs/LIBRARY.md) first.
Create the four mandatory lifecycle labels, replacing `example/project` with the
repository you control (these commands intentionally create/update labels):

```sh
gh label create 'status:ready' --repo example/project --color 238636 --description 'Eligible for Graph selection' --force
gh label create 'status:in-progress' --repo example/project --color 0969DA --description 'Claimed by a worker' --force
gh label create 'status:awaiting-merge' --repo example/project --color 8250DF --description 'Implementation awaits PR disposition' --force
gh label create 'status:blocked' --repo example/project --color D93F0B --description 'Unmet dependency or authority gate' --force
```

Before dispatch, explicitly check repository access and all four lifecycle labels:

```sh
python3 -B watcher.py repo check example/project
python3 -B watcher.py repo check example/project --json
python3 -B watcher.py repo check --json  # enrolled repositories only
```

This is an authenticated network read through `gh`, separate from accounts-free
`doctor`. An explicit target need not be enrolled and the check never enrolls it.
Metadata and label reads report separately: missing labels differ from unknown
labels after access denial, rate limiting, unavailable reads or the 1000-label
read cap. GitHub can hide inaccessible repositories behind 404; that result cannot
distinguish absence from denied access. Exit status is 1 for read failures or
missing labels, 0 for configured readable targets (or no enrolled targets).
Only permission booleans actually returned by GitHub are shown; omitted rights
remain unknown. Read success does not grant write/merge authority or establish
issue eligibility. Check `gh auth status` and repository access privately after
read failures, and deliberately use the manual label commands above for missing
labels. The check never changes labels, enrollment, services or models.

Create one bounded real issue, mark it ready only when actionable, and verify no
competing claim/PR or unresolved dependency. Enrollment alone does not make all
issues executable. Use the existing independent public source history; never
import private producer objects, refs or runtime state (see [IMPORT.md](IMPORT.md)).

Linux foreground trial (substitute the authorized owner/repository):

```sh
python3 -B watcher.py repo add example/project
python3 -B watcher.py repo list
python3 -B watcher.py library
python3 -B watcher.py watch --once
```

Enrollment persists locally. `watch --once` can read GitHub and launch a real
coordinator; it is not a dry-run. For accounts-free testing use `ci/check.py`.
Concurrent `repo add`/`repo revoke` edits fail with a retry message instead of
overwriting another edit. Retry the failed command after the other editor finishes;
only a successful command confirms the change. A private config-side `.lock` file
is retained for coordination; `repo list` remains read-only. Revocation changes
discovery and does not terminate a surviving worker.
Native Mac/Windows runner commands, recovery gates and path defaults are in
PLATFORMS.md. Record real trusted SessionStart/SubagentStart/SubagentStop delivery,
actual worker edits/validation/PR, stop/drain and safe restart without a duplicate
claim. A simulated event or local Git commit cannot substitute for these facts.

## Optional Linux service and removal

Use only after the foreground/host checks on a disposable installation:

```sh
bin/graph install       # writes unit/link; does not start or enable
bin/graph start
bin/graph status
bin/graph status --details
bin/graph stop          # drain; never kill workers to speed up removal
# Wait for verified idle and reconcile surviving workers, then:
bin/graph uninstall
```

The unit is `graph-community.service` and CLI link is `~/.local/bin/graph`.
Linux install records the resolved absolute `VEZRYN_GRAPH_CONFIG`,
`VEZRYN_GRAPH_STATE` and `VEZRYN_GRAPH_LIBRARY` paths, including their defaults.
Use the same profile when enrolling repositories and installing, starting,
stopping or uninstalling the service. For example, export these before the
commands above and keep them selected for later control:

```sh
export VEZRYN_GRAPH_CONFIG="$HOME/graph profile/repos.toml"
export VEZRYN_GRAPH_STATE="$HOME/graph profile/state"
export VEZRYN_GRAPH_LIBRARY="$HOME/graph profile/library"
```

Mismatched controls fail before writing the other profile's state. To change
profiles, request drain with the installed profile, wait for verified idle, then
install again with the new selection. Old PATH-only units have no verified
profile: controls refuse them rather than guessing. Identify the original
watcher's state path and request its stop marker before reinstalling while idle;
do not substitute the newly selected shell's state path. An owned unit changed on
disk also needs its loaded manager identity reconciled before control.

Foreign/modified installation entries or active/unknown services are refused.
Uninstall removes only owned unit/link, preserving source, enrollment, config,
journals, claims and worktrees. Failed manager reload rolls back owned files;
a failed rollback reload leaves manager state explicitly unverified. Fix manager
access and retry. Do not remove source until all workers and dependent users exit.
Unsupported control characters, undecodable paths, trailing source whitespace or
trailing backslash are rejected. See PLATFORMS.md for native Mac/Windows removal.

## Native macOS arm64 control

After the local check and trusted-client qualification, from the runtime copy:

```sh
python3 -B graph_macos.py repo add example/project
python3 -B graph_macos.py install
python3 -B graph_macos.py start
python3 -B graph_macos.py status --json
python3 -B graph_macos.py stop
# Wait for verified idle and reconciled ownership:
python3 -B graph_macos.py uninstall
```

Use the same Python, source path and explicit profile environment throughout.
Install captures the environment for the user LaunchAgent; inspect it before
starting. Do not switch profiles beneath an installed runner.

## Native Windows 11 x64 control (qualification only)

The separate native Windows VM trial is bounded evidence, not release approval.
This candidate includes its accepted fixes and native `commandWindows` hook
override. After the local check, and only after trusted native hooks, accounts
and ownership checks have passed in the intended test environment:

```powershell
& $Python -B .\graph_windows.py repo add example/project
& $Python -B .\graph_windows.py install
& $Python -B .\graph_windows.py start
& $Python -B .\graph_windows.py status --json
& $Python -B .\graph_windows.py stop
# Wait for verified idle and reconciled ownership:
& $Python -B .\graph_windows.py uninstall
```

Start manually after login/reboot; no automatic startup is installed. A local
smoke or successful install does not establish trusted hooks or online delivery.
Windows hook events now live in the protected state root, outside the writable
checkout. Existing `.graph/subagent-events.jsonl` history blocks operation until
its ownership is reconciled; no migration is automatic. Never delete unresolved
state to make start or uninstall succeed.

### Identify local source

Run `bin/graph version` (or `python3 -B graph_update.py version`) for a readable
source report; add `--json` for schema version 1. The macOS and Windows wrappers
forward the same command. `check-update` reports the same local identity and
continues to report that no reviewed update origin is available.

The report includes the local Git revision and dirty state when available. An
archive has no Git revision or dirty-state evidence, even inside another checkout.
The manifest SHA256 identifies the manifest bytes. `verified` means the source
payload matches the existing archive checker's file, hash, mode and content rules;
`invalid`, `missing` and `unavailable` do not establish a matching payload.
This is local consistency evidence, not publisher authentication. A manifest and
payload can both be changed. Git dirtiness and manifest verification are separate.
A failed Git read produces unknown values rather than claiming a clean checkout.

Release version remains unknown; release-note filenames do not establish it.
This report identifies the files on disk, not a running watcher, active source,
service health or platform qualification. It reads local files and Git only and
makes no network, service, account or model calls.
