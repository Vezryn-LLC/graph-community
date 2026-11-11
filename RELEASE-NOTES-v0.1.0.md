# Graph Community v0.1.0 — proposed release notes

## What Graph Community does

Graph Community is a headless, user-operated GitHub engineering orchestrator.
It watches explicitly enrolled repositories for actionable issues and launches
the native Codex CLI as a coordinator. That agent can claim work, delegate
native workers in isolated worktrees, validate changes and produce ordinary
GitHub pull requests. Graph provides durable ownership, conservative recovery,
private local state and editable generic Markdown workflow guidance.

Graph Community does **not** include a graphical application, a model,
subscriptions, credentials, hosted compute, company-private playbooks,
telemetry or an automatic source updater. It does not override user permissions
or guarantee that an agent's implementation is correct.

## Getting started

Required: Python 3.11+, Git, GitHub CLI, an installed native Codex CLI,
user-provided authenticated access, trusted lifecycle hooks and explicit
repository enrollment. Start at [QUICKSTART.md](QUICKSTART.md) and
[PLATFORMS.md](PLATFORMS.md).

For a first test, enroll only a disposable private repository.
`python3 -B ci/check.py` performs local accounts-free checking.
`watch --once` is **live** and may dispatch actual agent work.

## Observed platform qualification

| Platform | Witnessed scope | Limits |
| --- | --- | --- |
| Linux x64 | Native issue-to-worker-to-validated-PR, lifecycle events, user-service controls, surviving coordinator, inherited lock exclusion, safe recovery and no duplicates | Linux reboot recovery not claimed; verified for tested client and host |
| macOS arm64 | Native installation/control, issue-to-worker-to-PR, trusted callbacks, graceful stop, interruption and reboot/login | Other architectures and client versions not qualified |
| Windows 11 x64 | Actual native VM issue-to-worker-to-PR, hooks, exclusive native handle, competing-watcher refusal and graceful drain/restart | Startup remains manual; Windows reboot recovery and arm64 not qualified |
| WSL2 | No native qualification | Not a substitute for native Windows evidence |

Linux/macOS now resolve Codex's native executable where applicable so an npm
Node launcher cannot silently lose the inherited watcher lock; unknown wrappers
fail closed. Accepted Windows ownership/hook/private-journal fixes are included.
These are bounded host observations, not universal compatibility guarantees.

## Safety and operational limitations

The operator supplies GitHub/Codex permissions, infrastructure and account
capacity. Graph may create branches, worktrees, commits, issues and PRs in
enrolled repositories within those permissions. Unknown native ownership,
unreadable journals and ambiguous claims should remain held until reconciled;
do not erase state to force dispatch. No automatic source activation, hosted
control plane or Graph Community desktop UI is included. Review
[SECURITY.md](SECURITY.md) for private vulnerability reporting to
security@vezryn.com.

## License

Licensed under the [Apache License, Version 2.0](LICENSE). The scoped third-party
inventory is documented in [LICENSE-REVIEW.md](LICENSE-REVIEW.md); no specific
upstream NOTICE obligation was found for this candidate.

These are **proposed v0.1.0 release notes**, not a publication announcement.
The final public repository name, exact release commit and explicit publication
authorization have not yet been confirmed.
