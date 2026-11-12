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

## Local check, without accounts or services

From the runtime copy on Linux or Mac:

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
A passing smoke proves only the operations named in its output.

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

## Look at current candidates without dispatch

After enrolling repositories, use `python3 -B watcher.py queue` (or `queue --json`)
to read their current open `status:ready` metadata through your authenticated
GitHub CLI. Linux CLI users can also run `bin/graph queue`. This command makes no
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
