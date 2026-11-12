# Graph Community

**From ready GitHub issues to ordinary pull requests, using native Codex.**

Graph Community is a headless, open-source engineering coordinator for repositories
you explicitly enroll and are authorized to work in. Bring a bounded issue and
your own GitHub/Codex tools; Graph watches for actionable work, then lets native
Codex coordinate implementation and verification through your existing PR workflow.

**[Try the Quickstart](QUICKSTART.md)** ·
[Latest public release](https://github.com/Vezryn-LLC/graph-community/releases/latest) ·
[Architecture](ARCHITECTURE.md) · [Platform limits](PLATFORMS.md) ·
[Contribute](CONTRIBUTING.md) · [Wiki](https://github.com/Vezryn-LLC/graph-community/wiki)

The [Wiki](https://github.com/Vezryn-LLC/graph-community/wiki) teaches a first
workflow, enrollment/readiness, library customization and recovery. Canonical
installation, platform and security references remain in this repository;
[reviewed tutorial sources](docs/wiki/Home.md) and the
[upkeep convention](CONTRIBUTING.md#documentation-upkeep) keep corrections in the
ordinary contribution and release workflow.

## How work moves

```text
Enrolled repo + ready issue
             ↓
Codex reads + claims original issue
             ↓
Isolated workers implement + check
             ↓
Ordinary GitHub PR + recorded outcome
```

- **Keep the work in GitHub.** Original issues, claims, blockers and PRs remain
  the record; no hosted control plane is required.
- **Use native Codex workers.** The coordinator delegates independent work and
  reconciles ownership and results. Actual capacity depends on your client/account.
- **Adapt the workflow in Markdown.** The [engineering library](docs/LIBRARY.md)
  supplies editable playbooks, skills and policies rather than another model API.

[See the Graph workflow film](https://vezryn.com/products/graph/#film).
It uses illustrative interface footage to explain the flow; it is not an
authenticated terminal recording or proof of a particular delivery.

## Try it or help improve it

Start with the Quickstart's [accounts-free local check](QUICKSTART.md#local-check-without-accounts-or-services).
Real GitHub work additionally needs your authenticated tools, permissions and
qualified native client. Enrollment limits discovery; it grants no access, and
opening an issue does not automatically enqueue a worker.

For a small contribution, read [the contributor onramp](CONTRIBUTING.md#small-ways-to-start),
check [open issues](https://github.com/Vezryn-LLC/graph-community/issues) and
[existing PRs](https://github.com/Vezryn-LLC/graph-community/pulls), then propose
one focused change. Reports and documentation fixes are welcome without running
Codex or knowing the maintainer lifecycle labels.

## Releases and included source

Graph Community is public at `Vezryn-LLC/graph-community`, licensed under
[Apache-2.0](LICENSE). The immutable [v0.1.0 release](https://github.com/Vezryn-LLC/graph-community/releases/tag/v0.1.0)
is the baseline. v0.1.1 adds the engineering library, readable public-safe claims
and contributor instructions. No account, repository permission, model entitlement
or trusted client capability is bundled.

Read the generic [AGENTS.md](AGENTS.md) before real assignments.
[Smoke commands](SMOKE-MATRIX.md) and an inert
[CI example](ci/smoke.yml.example) describe qualification, not promised support.
[Contributing](CONTRIBUTING.md), [security reporting](SECURITY.md),
[independent-history rules](IMPORT.md), the historical
[v0.1.0 notes](RELEASE-NOTES-v0.1.0.md) and
[v0.1.1 notes](RELEASE-NOTES-v0.1.1.md) describe the source and release boundaries.
The default [engineering library](docs/LIBRARY.md) contains 22 playbooks, 10 skills
and six policies; see its [inventory and source review](docs/GUIDANCE-REVIEW.md).

## Boundaries and platform evidence

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
