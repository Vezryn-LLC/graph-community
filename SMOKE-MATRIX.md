# Minimal smoke matrix

`ci/smoke.yml.example` is inert: it is outside `.github/workflows` and has an
`.example` suffix. No CI has been activated or billed. Its only trigger, if a
future owner deliberately installs it, is manual workflow_dispatch. Review
account permissions/billing and pin reviewed action revisions first.

| Target | Example runner | Exact command from fresh payload copy | Evidence it can provide / cannot provide |
| --- | --- | --- | --- |
| Linux x64 | ubuntu-24.04 | `python3 -B ci/check.py` | Manifest/import/local process and inherited lock smoke. No real systemd, credentials, hooks or remote PR. |
| macOS arm64 | macos-15 (verify arm64 at execution) | `python3 -B ci/check.py` | Native local primitives when actually executed. No interactive GUI launchd, trusted client session or real PR proof. |
| Windows hosted x64 | windows-2025 | `python -B ci/check.py` | Server image imports/native primitives when executed. **Not Windows 11** and not authenticated native client/hook proof. |
| Native Windows 11 x64 | Authorized user's real native session | `& (Get-Command python.exe).Source -B .\ci\check.py` | Actual Windows 11 local primitives if observed; additional user/client/repo tests still required. |

Runner labels/architectures must be checked before activation against
[GitHub's current runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
Standard hosted Windows x64 images are Server editions, so a green hosted job
cannot satisfy the Windows 11 target. The checker rejects unexpected architecture
when the example's EXPECT_ARCH is set. An unavailable label is not a test result.

For a manual Linux/Mac terminal, set `EXPECT_ARCH=x86_64` / `EXPECT_ARCH=arm64`
respectively before the command if asserting architecture. Windows x64 uses
`$env:EXPECT_ARCH='AMD64'`. Record OS edition/version, Python, native client and
manifest identity with the output. CI adds no credentials, gh/Codex install,
service install, enrollment or model calls. `ci/check.py` is a local dry-run;
`watch --once` is live execution and is never used in the example.

Actual authorized host installation commands are in QUICKSTART.md / PLATFORMS.md:
Linux `bin/graph install/start/status/stop/uninstall`; Mac `python3 -B
graph_macos.py install/start/status --json/stop/uninstall`; Windows native
`python.exe -B graph_windows.py install/start/status --json/stop/uninstall`
(run one action at a time; the slashes above denote alternatives). Install/start
must use the appropriate real user session, with zero production enrollment.

Further interactive qualification needs the intended native client and an
authorized disposable PRIVATE GitHub repo; reuse the existing controlled fixture
when appropriate: verify trusted hook
loading and actual SessionStart/SubagentStart/SubagentStop; then one issue →
claim → native worker → validation → remote PR. Observe stop/drain, surviving
coordinator, safe restart/no duplicate, uncertain journals/identity and owned
reinstall/uninstall. Mac also needs real launchd/ACL/logout/reboot observations;
Windows needs actual ACL/handle inheritance and manual login/reboot recovery.
Do not log in remotely or authenticate on someone's behalf under this preflight.

Authenticated Linux issue-to-PR and trusted lifecycle delivery are already
witnessed. Separate isolated Linux surviving-coordinator / competing-watcher,
lock/state recovery and no-duplicate witnesses are complete. This candidate
includes the native launcher correction used in the remaining inherited-lock
witness. Validate source applicability; do not replay completed worker trials. Separate macOS arm64
and Windows 11 x64 VM results are summarized in PLATFORMS.md. This candidate
includes the accepted Windows repairs, but Linux-hosted recipient regressions
are not fresh native qualification. Linux/Windows reboot and broader host/client
coverage remain unclaimed. No paper subtask or simulated event satisfies them.
