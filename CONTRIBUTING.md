# Contributing

Graph Community is public under [Apache-2.0](LICENSE). Contributors must have
rights to their changes and preserve applicable copyright/license notices.
No CLA, DCO or assignment policy is implied. Read [AGENTS.md](AGENTS.md), the
[engineering policy](policies/ENGINEERING.md) and [library guide](docs/LIBRARY.md).

Start from the original issue and an isolated branch/worktree. Implement the
smallest useful change, reuse existing coverage and verify affected behavior.
Routine changes need no independent model reviewer. Material authorization,
credential, irreversible or hard-to-validate risks require targeted review.
Report actual versus simulated evidence and remaining limitations in the PR.
Security vulnerabilities go privately to the route in [SECURITY.md](SECURITY.md).

Before proposing payload changes, deliberately update the reviewed positive
allowlist in `ci/check.py` only for approved source paths. Regenerate
`MANIFEST.json` file hashes/modes after intentional edits; it covers every payload
file except itself. Run `python3 -B ci/check.py` on the exact clean source.
The checker runs local guidance regressions, document links and primitive smoke;
it does not authenticate, start a service or call a model.

Do not add private source, personal data, credentials, operational logs/state,
product profiles or unrelated history. Reuse this repository's independent Git
history. The [source/notice inventory](docs/GUIDANCE-REVIEW.md) and
[license review](LICENSE-REVIEW.md) explain the newly shipped guidance. Reassess
provenance and include actual upstream notices for any new external material.

## Release preparation

Keep v0.1.0 and its artifacts immutable. This follow-up targets v0.1.1 and prepares
one reviewable library update. A merged PR is not release authorization. Record
exact source/manifest identity, changed behavior and applicable evidence before
an owner-authorized tag/release. Source activation remains unavailable.

Reuse valid native platform evidence when contracts are unchanged; do not replay
qualification just for Markdown additions. Recheck an affected boundary when a
runtime change invalidates earlier evidence. Do not enable paid CI, change
repository visibility, deploy or grant account access without that action's
specific authority. No package registry or new release engine is needed.
