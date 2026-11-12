# Enrollment and issue readiness

Enrollment, eligibility and permission answer different questions. Keeping them separate makes it easier to understand an idle coordinator.

| Question | Source of truth |
| --- | --- |
| Which repositories does this watcher discover? | The local enrolled repository list for its selected profile |
| May a new issue be considered? | An open issue with `status:ready`, plus current dependencies, ownership, PRs and scope |
| What may the agent actually do? | The operator's authority, authenticated tools, repository rules and standing instructions |
| What was delivered? | Actual issue/PR outcomes and validation or operational evidence |

## Choose a repository deliberately

Follow the [Quickstart's enrollment and foreground trial](https://github.com/Vezryn-LLC/graph-community/blob/main/QUICKSTART.md#one-real-issue-only-after-native-hostaccount-authorization). Inspect the list using the same profile that the installed runner uses. A different shell environment can select a different configuration; platform defaults and overrides are documented in [PLATFORMS.md](https://github.com/Vezryn-LLC/graph-community/blob/main/PLATFORMS.md).

Enrollment limits discovery. It neither creates GitHub credentials nor grants repository access, model entitlement or permission for a production action. Removing a repository from discovery is not authority to terminate its surviving worker.

## Decide whether the next step is ready

An authorized maintainer should make the original issue specific enough to act on, verify prerequisite delivery, and check for a competing claim or PR before applying `status:ready`. Contributors can report problems without knowing or setting Graph labels.

The coordinator still checks the original issue and current context. A ready label does not override `status:blocked`, an in-progress owner, an awaiting-merge PR or a genuine authority boundary. A closed prerequisite alone may not prove accepted delivery.

| Recorded state | What to look for next |
| --- | --- |
| `status:ready` | Coordinator qualification and a real claim if selected |
| `status:in-progress` | The accountable worker's current source and progress |
| `status:awaiting-merge` | The actual PR and its required disposition |
| `status:blocked` | Exact unmet gate, next owner/action and clearing event |
| Closed | Delivered outcome or explicit non-delivery disposition; read the reason |

Use the public [selection policy](https://github.com/Vezryn-LLC/graph-community/blob/main/policies/ISSUE_SELECTION.md) and [lifecycle policy](https://github.com/Vezryn-LLC/graph-community/blob/main/policies/ISSUE_LIFECYCLE.md) for the precise contract. Do not repeatedly toggle readiness to bypass recovery or ownership evidence. Resolve the actual blocker, then let the ordinary lifecycle record the next eligible step.
