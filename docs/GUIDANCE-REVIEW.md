# Guidance inventory and source review

This follow-up inventories the maintained source catalog of 31 playbooks,
23 skills and seven policies. Those counts describe inputs, not the payload.
The selected Community default is **22 playbooks, 10 skills and six policies**.
Attribution: Vezryn Graph contributors, original engineering guidance; Community
adaptations remove private operational dependencies and retain the generic method.
The existing Apache-2.0 [LICENSE](../LICENSE) is unchanged. See the scoped
[notice review](../LICENSE-REVIEW.md); source selection is not a legal guarantee.

## Included engineering playbooks

These workflows retain the actual source method, including original-task intent,
focused verification, normal GitHub delivery, interruption recovery and exact
source-retirement proof. Generic completion wording now refers to existing native
capabilities. The former single `deliver.md` duplicates normal delivery and is
replaced by the intent-specific routes below.

| Canonical path | Purpose |
| --- | --- |
| `playbooks/architecture-decision.md` | A concrete engineering tradeoff needs a decision. |
| `playbooks/autonomous-issue-to-pr.md` | An authorized GitHub issue must become a real delivered PR. |
| `playbooks/benchmark-and-optimize.md` | An issue requests measurable performance or cost improvement. |
| `playbooks/context-handoff.md` | Active work needs a coordinator or worker context handoff. |
| `playbooks/diagnose-and-repair.md` | bugs, regressions and production behavior that is demonstrably broken. |
| `playbooks/document-and-verify.md` | documentation, runbooks, instructions, examples and policy edits. |
| `playbooks/implement-and-deliver.md` | actionable features and scoped improvements. |
| `playbooks/independent-review.md` | Specific consequential risk or an explicit request warrants review. |
| `playbooks/integrate-and-verify.md` | Previously implemented components must work together. |
| `playbooks/investigate-and-recommend.md` | Research or technical investigation is requested without implementation. |
| `playbooks/issue-triage.md` | An issue needs priority, duplicate, blocker or applicability assessment. |
| `playbooks/launch-and-observe.md` | The request is to launch an existing program or check. |
| `playbooks/maintain-and-refactor.md` | An issue needs cleanup, maintenance or removal of obsolete code. |
| `playbooks/orchestrate-work.md` | Independent issues can be delegated to Codex workers. |
| `playbooks/pause-and-recover.md` | Quota interruption, user stop or worker failure requires continuity. |
| `playbooks/pr-maintenance.md` | An existing PR needs focused fixes, rebase or completion. |
| `playbooks/prepare-draft-pr.md` | An implemented change needs publishing as a PR. |
| `playbooks/rapid-prototype.md` | new product ideas, UX concepts and speculative experiments. |
| `playbooks/release-and-disposition.md` | A completed PR or build needs merge or release disposition. |
| `playbooks/repair-and-resume.md` | Recoverable issue work was interrupted. |
| `playbooks/smoke-test.md` | The task calls for a quick representative functional check. |
| `playbooks/worktree-retirement.md` | A known issue-owned temporary worktree reaches closeout, including a late PR merge. |

## Included skills

All ten generic engineering skills are retained. The cross-repository verification
skill now directs workers to actual producer/consumer source and pinned contracts,
replacing a private-only interface-map reference. It adds no universal test matrix.

| Canonical path | Purpose |
| --- | --- |
| `skills/agent-orchestration/SKILL.md` | Coordinate multiple workers without recreating Codex's scheduler. |
| `skills/change-aware-verification/SKILL.md` | Select proportionate tests and empirical evidence for actual changed behavior. |
| `skills/context-continuity/SKILL.md` | Keep tasks resumable across context, process and quota changes. |
| `skills/execution-intent-preservation/SKILL.md` | Keep the requested outcome ahead of speculative engineering. |
| `skills/independent-engineering-review/SKILL.md` | Review consequential risks only when warranted. |
| `skills/observable-progress/SKILL.md` | Report meaningful evidence rather than performative activity. |
| `skills/outcome-driven-engineering/SKILL.md` | Keep delivery focused on a working, observable outcome without ceremony. |
| `skills/prototype-first/SKILL.md` | Build a small runnable experiment before production architecture. |
| `skills/repair-and-resume/SKILL.md` | Repair ordinary failures and continue the original task instead of creating recovery bureaucracy. |
| `skills/source-custody/SKILL.md` | Protect concurrent Git work using normal Git tooling. |

## Policies

| Path | Treatment |
| --- | --- |
| `policies/ISSUE_SELECTION.md` | Retain existing Community selection/authority/dependency policy |
| `policies/ISSUE_LIFECYCLE.md` | Retain existing Community claims, recovery and retirement policy |
| `policies/ENGINEERING.md` | Retain existing Community proportional verification/review policy |
| `policies/MODEL_ROUTING.md` | Adapt generic capability checks, configured defaults and safe fallback; no private model preferences |
| `policies/ROUTING_MATRIX.md` | Adapt intent-based examples to the actual shipped catalog; no creative/private-product routes |
| `policies/DELEGATION.md` | Adapt complete literal assignment, independent source ownership and continuity; exclude private receipt/instrumentation integrations |

## Excluded source guidance

| Source paths | Reason |
| --- | --- |
| `playbooks/creative-{establish-direction,compose-and-prototype,critique-and-refine,choreograph-interaction,extend-identity,finish-and-check-readiness,write-with-personality}.md` (seven files) | Creative/product direction and rendering workflow need separate source, external-concept and product-context review; outside this engineering default |
| `skills/creative-{accessibility-check,art-direction,brand-voice,design-system,form-audit,launch-checklist,motion,page-composition,remove-ai-writing,theme-switch,tidy-up,visual-critique}/SKILL.md` (12 files) | Creative methods, including external concept lineage, excluded with their routing and product evidence |
| `policies/CREATIVE_ROUTING.md` | Product/model-specialist creative routing is not needed for generic engineering delivery |
| `playbooks/founder-preview.md` | Product-owner-specific preview route; generic prototypes already provide a usable artifact and feedback path |
| `playbooks/plan-large-delivery.md` | Experimental multi-increment planning contains private diagnostic/process dependencies; not required for these bounded execution routes |
| `skills/vezryn-engineering-router/SKILL.md` | Product-named router duplicates generic native model and task-routing policies; do not add another router layer |

This accounts for all 31 source playbooks, 23 source skills and seven source
policies. Source product profiles, private root instructions, research/sales data,
model configuration, tests with private context, historical objects, hooks/logs
and operational evidence are not public payload inputs. No private repository
identity or source revision is needed to use this default library.

## Provenance and notice scope

The newly selected engineering bodies were read and compared with retained pstack
source, including its MIT license and harness-neutral mirror documentation.
No pstack implementation, instruction body, distinctive passage, asset or example
was selected. Shared general engineering concepts and short generic phrases do
not establish copied material. The selected bodies contain no identified specific
third-party copyright/license header or substantial matching passage requiring a
new notice. No new MIT notice is indicated for this selected payload. Excluded
creative material has separate external concept lineage and is not cleared here.

The review covered the new guidance and the adapted Community policies/docs,
not merely the earlier 28-file review. Private input hashes, comparison output and
source lineage are retained outside this repository; no private Git objects,
refs, account records or review transcripts are imported. Reassess and include the
actual copyright/permission notices if later changes introduce external material.
The package checker screens known markers; neither matching nor absence of a
signature certifies exhaustive provenance, privacy or legal title.
