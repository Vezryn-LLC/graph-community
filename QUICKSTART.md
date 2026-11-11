# Beginner quickstart (private evaluation)

Use only an authorized disposable private workspace. This source includes
[Apache-2.0](LICENSE), but has no published installer, public repository,
model account, or authentication flow. Keep the original manifest/source
pristine and copy it into a separate runtime directory before trying commands.

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
python3 -B watcher.py capabilities
python3 -B smoke.py
```

On native Windows PowerShell:

```powershell
$Python = (Get-Command python.exe).Source
& $Python --version
& $Python -B .\ci\check.py
& $Python -B .\watcher.py capabilities
& $Python -B .\smoke.py
```

`ci/check.py` checks manifest bytes/completeness, compiles Python in memory, imports
entrypoints and executes the local primitive smoke in fresh temporary state. It
uses no GitHub/Codex credentials, enrollment, service manager or model call.
A passing smoke proves only the operations named in its output.

## One real issue, only after native-host/account authorization

Use an authorized disposable PRIVATE test repository with no production data;
reuse an existing qualification repository when appropriate rather than creating
a duplicate. Read
AGENTS.md and policies first. In that test repo create `status:ready`,
`status:in-progress`, `status:awaiting-merge`, `status:blocked` labels using normal
GitHub tools; make one bounded test issue ready. Verify no competing claim.
If the client requires source Git trust, use only fresh private Git history as
in IMPORT.md, never the original repository's objects/remotes.

Linux foreground trial (substitute the authorized owner/repository):

```sh
python3 -B watcher.py repo add example/project
python3 -B watcher.py repo list
python3 -B watcher.py watch --once
```

Enrollment persists locally. `watch --once` can read GitHub and launch a real
coordinator; it is not a dry-run. For accounts-free testing use `ci/check.py`.
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
