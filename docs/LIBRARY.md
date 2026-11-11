# Default engineering library

Graph Community ships 22 engineering playbooks, 10 skills and six coordinator
policies. They are Markdown instructions for native Codex, not plugins, an
execution engine or a model API. A fresh install needs no user overrides to
route feature, bug, prototype, docs, research, integration, PR repair, validation
and recovery work. See [the complete inventory and review](GUIDANCE-REVIEW.md).

## First assignment

Read [the quickstart](../QUICKSTART.md), authenticate your own GitHub/Codex tools,
create the four lifecycle labels and enroll a repository you control. Run:

```sh
python3 -B watcher.py repo list
python3 -B watcher.py library
python3 -B watcher.py watch --once
```

`watch --once` is live and may create real engineering work. `ci/check.py` is the
accounts-free local check. Enrollment is empty by default and limits discovery,
not credential scope or termination of active workers. No account, worker
capability or model entitlement is included.

The coordinator reads the actual ready issue and all current ownership/dependency
context. [Routing examples](../policies/ROUTING_MATRIX.md) suggest one primary
playbook and 1–3 useful skills. [Model selection](../policies/MODEL_ROUTING.md)
checks the installed client, preserves capable configured defaults and falls back
to supported native settings. Priority is urgency, not reasoning difficulty.
For example, a scoped feature normally uses `implement-and-deliver` and
`change-aware-verification`; an observed regression uses `diagnose-and-repair`.

The worker receives the complete original issue and **literal selected Markdown**,
implements in an isolated branch/worktree, verifies actual behavior and completes
the ordinary GitHub lifecycle. Read [delegation](../policies/DELEGATION.md).
Recommendations do not guarantee quality, concurrency or successful delivery.
Native/global/project instructions and the user's authority remain applicable.

## Overrides and disable markers

The default override root is `library/` beside the selected repository config;
normally `~/.config/graph-community/library/`. `VEZRYN_GRAPH_CONFIG` selects the
config file; `VEZRYN_GRAPH_LIBRARY` explicitly selects a different library root.
Platform-specific defaults are in [PLATFORMS.md](../PLATFORMS.md). The historical
`VEZRYN_GRAPH_*` environment variable names remain compatibility inputs.

Only these shapes are read: `policies/*.md`, `playbooks/*.md`,
`skills/*/SKILL.md`. A local file at the same relative path completely replaces
its default; it is not a patch or merged prompt. New names add local guidance.

```sh
mkdir -p ~/.config/graph-community/library/playbooks
# Write your complete local replacement to this path:
$EDITOR ~/.config/graph-community/library/playbooks/implement-and-deliver.md
# Or hide an optional default (or its replacement):
touch ~/.config/graph-community/library/playbooks/rapid-prototype.md.disabled
python3 -B watcher.py library
```

Precedence is `.disabled` marker > local file > bundled file. Marker contents
are irrelevant. Delete the marker to re-enable; remove a replacement to restore
the default. Recommendations cannot resurrect disabled files. If missing
essential guidance prevents safe work, Codex explains and defers that assignment.
A library marker cannot erase standing instructions already supplied by Codex.

Changes are read on the next coordinator launch. Drain existing work before
changing guidance that must take effect consistently; service environment overrides
must be set in that service, not just an unrelated shell. Graph does not write
user overrides, install these skills globally or change Codex settings. Source
activation remains unavailable; use the existing reviewed manual installation
process. Preserve overrides, config and in-flight ownership during replacement.

## Verification limits

`python3 -B ci/check.py` verifies the positive payload allowlist, manifest bytes
and modes, known private-data markers, independent Git roots when Git metadata is
present, local documentation links and existing accounts-free primitive checks.
It also runs `ci/test_library.py`: a fresh synthetic home, replacement/disable
precedence, installation replacement preserving overrides, custom roots and
literal selected guidance through the real launcher to a fake client process.
The test explicitly substitutes executable discovery; it does not qualify native
binary detection, model judgment, account access, trusted hook delivery or a live
GitHub task. The runtime modules are unchanged by this library update.
