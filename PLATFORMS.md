# Platform limits and host qualification

| Target | Implemented source | Observed evidence / remaining gate |
| --- | --- | --- |
| Linux | Shared watcher, POSIX inherited flock, process birth evidence, user-service CLI | Actual isolated local Python/Git/process/lock/drain/recovery and user-manager install/start/drain/uninstall. Separate authenticated native sessions delivered trusted lifecycle events and real issue→worker→validated remote PRs. Separate isolated witnesses completed surviving-coordinator, competing-watcher exclusion, lock/state recovery and no-duplicate checks. The npm Node launcher lost the inherited lock; this candidate includes the native executable correction used by the accepted remaining lock witness. Recipient checks establish source applicability, not a replay of every native trial. Completed worker deliveries must not be replayed. Linux reboot is not claimed. |
| macOS arm64 | Python user LaunchAgent, POSIX ownership, native birth identity and ACL checks | Witnessed isolated native install/control, trusted lifecycle, issue→worker→validated unmerged PR, graceful stop, abrupt watcher interruption without duplicate dispatch, and one reboot/login. The accepted post-reboot launchd parser correction is included in this candidate. These bounded results do not qualify x86_64 or every client/OS version. |
| Windows 11 x64 native | Experimental manual detached Python runner, native exclusive/inherited handles, process creation identity and protected ACLs | A separate isolated Windows 11 x64 VM witnessed native install/reinstall/start/duplicate-start/stop/uninstall, authenticated issue→native coordinator→one worker→one open unmerged PR, real hook callbacks/matching stop, inherited Codex lock/competing-watcher refusal and two graceful drain/restart cycles. This candidate incorporates the accepted OWNER RIGHTS, native hook command and private-state journal repairs. Its recipient checks are Linux-hosted, not a new native trial; original missing delivery-window events remain missing. Automatic startup and source update unavailable. Reboot recovery and arm64 unqualified. |
| WSL2 | Separate prospective Linux fallback | No WSL host result. WSL/Linux simulation is not native Windows proof. |

No Mac or Windows support claim follows from importability or simulated checks.
`source_update` is unavailable everywhere; `native_hooks` is unverified. The
package excludes optional private metrics/attribution/usage writers and all
graphical code. Native capacity/account permissions are external prerequisites.

Default config/state roots:

- Linux: `~/.config/graph-community/repos.toml`, `~/.local/state/graph-community`.
- Mac: `~/Library/Application Support/graph-community/repos.toml`, `state/` below
  that root; agent label `org.graph.community`.
- Windows: `%LOCALAPPDATA%/graph-community/repos.toml`, `state/`; native CLI entry
  under the config parent's `windows-runner/` directory.

Explicit `VEZRYN_GRAPH_*` compatibility overrides take precedence. Use absolute
paths containing spaces in qualification. Linux/macOS hook journals remain source-local
`.graph/subagent-events.jsonl`. Windows ownership events use the protected state
root's `subagent-events.jsonl`, outside the writable source checkout. Existing
Windows source-local history causes a fail-closed reconciliation error; it is
never silently moved, ignored or erased. Preserve and reconcile that history
before using this source. Keep pristine manifest/source separate from runtime copies.

Linux user-service control still requires Bash/GNU utilities/systemd; foreground
Python does not require a service install. User install creates files/link without
starting or enabling a service. Stop requests drain; it does not kill workers.
The source path should be checked against the real service's quoting/identity
requirements before installed use.

Mac install requires Python 3.11+, Git/gh/Codex and the user's GUI launchd domain,
with no administrator changes. Explicit argv/environment, restrictive permissions,
no extended ACL, matching loaded agent/working directory/configuration and precise
birth identity are checked conservatively. Unknown output remains unknown.
AbandonProcessGroup/exit-timeout behavior after logout/reboot must be observed on
the actual host. Uninstall only unloads verified idle owned configuration after
runtime exclusion and complete ownership reconciliation.

Windows requires native Python, `git.exe`, `gh.exe`, `codex.exe` on absolute PATH
entries. Batch shims/current-directory lookup are unavailable. It installs only a
private manifest/Python entry, without Task Scheduler, registry, PATH or startup
changes. Start is manual after login/reboot. A protected startup intent precedes
process creation; unresolved/failed/malformed intent blocks duplicates. PID plus
creation time, image, launch metadata and runtime handle are checked. Unknown
session holds survive restart and later empty journals. Stop writes a marker;
uninstall preserves all operational evidence and never ends tasks or children.

Windows private directories are current-user/SYSTEM protected DACLs. Existing
files require native ownership/ACL/identity checks. Unsafe ancestry, unknown ACEs,
SID bounds, reparse/junction/hardlink paths and non-fixed/local-drive routes fail
closed. POSIX chmod is not ACL validation. A missing or denied native API does not
authorize a weaker fallback.

## Isolated smoke and real-host sequence

On each **actually authorized native host**, copy the reviewed artifact privately
into a disposable runtime directory; inspect its manifest first. Run:

```sh
python3 -B watcher.py capabilities
python3 -B smoke.py
python3 -B watcher.py repo list
```

On Windows use native `python.exe` with PowerShell's `&` invocation as shown in
QUICKSTART.md. The smoke creates only temporary state and its own child, testing private
state, process lifetime and inherited exclusion after the parent closes its lock.
It reports local primitive execution, not a Codex client or supported platform.
The package checker alone supplies no native Mac/Windows evidence; native observations
above were separate controlled trials.

Before unattended work, qualify the intended native client's trusted hook loading
and actual SessionStart/SubagentStart/SubagentStop delivery. The POSIX command
requires explicit root/Python paths supplied by the watcher. The Windows client
uses the included reviewed `commandWindows` override: fixed PowerShell invokes
the explicit Python/root environment values without shell interpolation of their
contents. The separate Windows trial witnessed native delivery; each new client
and profile still requires supported hook trust and actual event verification. Never inject fake native IDs/events to fill missing evidence.

Read the generic policies, create the lifecycle labels using normal GitHub tools,
enroll only an authorized disposable repository, and make one bounded issue ready.
If the real Codex client requires Git trust, initialize a **fresh private** Git
repository for this clean source; import no old objects/remotes/history. Then use
the matching platform runner to demonstrate actual native worker→validation→PR.

Observe explicit stop/drain, surviving coordinator after watcher interruption,
safe restart/no duplicate claim, partial and unreadable journal, missing/PID-reused
identity, failed launch/start intent, permission/ACL/reparse problems, and owned
install conflicts/reinstall/uninstall. Inspect only test-owned known processes.
On Windows additionally verify actual inherited handle retention by the intended
Codex executable and rejection of a synthetic foreign ACL/hardlink. On Mac verify
actual launchd/ACL/birth-time semantics, including logout/reboot. Retain exact
source/manifest, OS/Python/client versions and actual versus simulated results.
Never restart production/founder services or delete unknown holds to manufacture
success. Rights/publication/activation remain separate decisions.
