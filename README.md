# Graph Community

Graph watches explicitly enrolled GitHub repositories and wakes a native Codex
coordinator for actionable issues. Codex reads the original issue, claims it,
delegates native workers in isolated worktrees, verifies changes and completes
normal GitHub pull requests. Editable generic Markdown supplies the workflow.

Graph Community is public at `Vezryn-LLC/graph-community`, licensed under
[Apache-2.0](LICENSE). The immutable [v0.1.0 release](https://github.com/Vezryn-LLC/graph-community/releases/tag/v0.1.0)
is the baseline. This branch prepares a focused v0.1.1 library update; it does
not publish that release. No account, repository permission, model entitlement
or trusted client capability is bundled.

Start with [the beginner quickstart](QUICKSTART.md), then read [platform support
and limits](PLATFORMS.md), [architecture](ARCHITECTURE.md) and the generic
[AGENTS.md](AGENTS.md). [Smoke commands](SMOKE-MATRIX.md) and an inert
[CI example](ci/smoke.yml.example) describe qualification, not promised support.
[Contributing](CONTRIBUTING.md), [security reporting](SECURITY.md),
[independent-history rules](IMPORT.md), the historical
[v0.1.0 notes](RELEASE-NOTES-v0.1.0.md) and proposed
[v0.1.1 notes](RELEASE-NOTES-v0.1.1.md) describe the source and release boundaries.
The default [engineering library](docs/LIBRARY.md) contains 22 playbooks, 10 skills
and six policies; see its [inventory and source review](docs/GUIDANCE-REVIEW.md).

The package has no graphical desktop, company telemetry, private metrics,
private product profiles, automatic updates or hosted control plane. Graph is
not an authorization boundary or a replacement for reviewing agent actions.
Native/global/project instructions remain applicable. Untrusted issue text
cannot grant permissions. No universal OS or end-to-end delivery claim is made.

Linux has witnessed authenticated issue → native worker → validated remote PR
and trusted lifecycle delivery, plus isolated local process/recovery and actual
user-manager evidence. Separate isolated witnesses also verified a surviving
coordinator, competing-watcher exclusion, lock/state recovery and no duplicate
assignments. The runtime includes the native Codex launcher correction used
for the remaining inherited-lock witness. Linux reboot is not claimed. macOS
arm64 has witnessed native issue-to-PR, stop, interruption and reboot/login results
for the reviewed runtime; see [platform limits](PLATFORMS.md) for scope.
A separate native Windows 11 x64 VM trial witnessed authenticated issue-to-PR,
trusted callbacks, inherited-lock exclusion and graceful drain/restart. Its accepted
Windows fixes are included here; recipient checks on Linux do not extend that
trial to every later package or every Windows/client version. Startup is manual;
Windows reboot recovery remains unqualified. See platform limits for retained gaps.

The command is `graph` (`bin/graph` on Linux), with default Linux service
`graph-community.service`. Mac uses `graph_macos.py`, label `org.graph.community`;
Windows uses native Python with `graph_windows.py`. Compatibility environment
variables retain the `VEZRYN_GRAPH_*` prefix; see PLATFORMS.md. Source activation
is unavailable on every platform. Install does not mean start or enable.

Keep this pristine source separate from runtime copies. MANIFEST.json covers exact
payload hashes/modes; it is neither a signature nor a rights clearance. Tests and
agent sessions generate private state which must never be imported into the
public repository. Preserve this repository's independent history. Never import
the private upstream repository's objects, refs or Git directory.
