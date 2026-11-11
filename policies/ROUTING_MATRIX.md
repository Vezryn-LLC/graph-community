# Select by the original task

Read the complete issue, comments, related PRs and current dependencies first.
Labels can be wrong: the requested operation and observable result determine the
route. Use one primary available playbook and only 1–3 useful available skills.
Read the effective inventory before following recommendations; missing or disabled
guidance cannot be silently restored from bundled defaults.

| Intent | Primary playbook | Useful skills | Relative starting effort, when supported |
| --- | --- | --- | --- |
| Feature or scoped improvement | `implement-and-deliver` | `outcome-driven-engineering`, `change-aware-verification` | medium |
| Bug or regression | `diagnose-and-repair` | `repair-and-resume`, `change-aware-verification` | medium; raise for hard reproduction or concurrency |
| Runnable experiment | `rapid-prototype` | `prototype-first`, `outcome-driven-engineering` | medium |
| Documentation | `document-and-verify` | `outcome-driven-engineering` | low; raise for deep API correctness |
| Investigation without implementation | `investigate-and-recommend` | `execution-intent-preservation`, `outcome-driven-engineering` | medium |
| Connect existing components | `integrate-and-verify` | `source-custody`, `change-aware-verification` | medium; raise for uncertain interfaces |
| Existing PR repair or rebase | `pr-maintenance` | `source-custody`, `change-aware-verification` | match the actual failure |
| Launch or validation | `launch-and-observe` | `execution-intent-preservation`, `observable-progress` | medium |
| Maintenance or removal | `maintain-and-refactor` | `source-custody`, `change-aware-verification` | medium; raise for risky migration |
| Interrupted task | `repair-and-resume` | `repair-and-resume`, `context-continuity` | match the remaining work |

Other available intents: `issue-triage`, `architecture-decision`,
`benchmark-and-optimize`, `smoke-test`, `prepare-draft-pr`,
`release-and-disposition`, `context-handoff`, `pause-and-recover`,
`orchestrate-work`, `autonomous-issue-to-pr` and `worktree-retirement`.
Select `independent-review` only for an explicit request or the consequential
risks in [ENGINEERING.md](ENGINEERING.md); routine delivery needs no second model.

[MODEL_ROUTING.md](MODEL_ROUTING.md) controls actual capability checks and fallback.
These effort examples do not promise that a setting exists or fits every task.
The coordinator records issue URL, selected/inherited configuration, one playbook,
skills and worker name in the existing claim. Keep exact worktree/source custody
in that claim for verified private repositories, or in the restricted local
record with a public-safe withheld field under [ISSUE_LIFECYCLE.md](ISSUE_LIFECYCLE.md).
Pass the original issue and literal selected guidance under
[DELEGATION.md](DELEGATION.md).

The default library covers engineering. Product-specific creative direction,
design profiles and experimental multi-increment planning are not shipped. Use
authorized repository guidance or local overrides for those objectives; absence
does not authorize importing private company material or inventing product scope.
