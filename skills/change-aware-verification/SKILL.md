---
name: change-aware-verification
description: Select proportionate tests and empirical evidence for actual changed behavior.
---

# Change-Aware Verification

- Read the diff, current behavior and existing coverage before creating more tests.
- Reproduce demonstrated bugs; verify the repair and meaningful affected integrations.
- Reuse valid evidence and existing tests; don't rerun unchanged broad suites without reason.
- Parameterize or consolidate overlapping cases; delete obsolete tests when their contract disappears.
- Separate simulated checks, integration checks and actual live behavior.
- Preserve required CI and meaningful security/data-integrity coverage even when extensive.
- Stop when the requested behavior and actual risks are adequately checked. No mandatory additional reviewer.

## Consumed interfaces across repositories

- Inspect the diff and actual call site when a change may affect a consumed contract:
  paths/requests, response fields/envelopes, enum/status meanings, defaults/bounds/
  pagination, authorization, idempotency/retry/transaction semantics or compatibility
  version declarations. Inspect the actual producer and consumer source; co-enrollment alone is not a
  dependency. Include the affected contract and pinned source links in the
  normal assignment packet when the worker cannot read the other repository.
- Only for an affected interface, run its producer boundary against the real consumer
  request/parser/adapter at exact source revisions. Reuse focused tests and
  producer-generated transport fixtures. Check the current supported/deployed
  consumer when known; record unknown identity rather than assuming it is `main`.
  Label synthetic, isolated runtime and hosted evidence accurately.
- Internal refactors with unchanged contracts, styling/static Website changes and
  unrelated files need no extra cross-repo check. Inspect uncertain boundary impact
  before deciding; no universal matrix, lock or reviewer is required.
- In the existing PR closeout record both SHAs, surface, command, actual pass/fail,
  supported/deployed-consumer coverage and limits. Before merge/release inspect
  whether the relevant interface changed on either side; rerun only impacted checks.
  Unrelated commits do not invalidate applicable evidence.
- A red pair is not compatible. Coordinate only the affected linked work using normal
  source ownership. Prefer expand → migrate consumers → retire old behavior with
  documented supported installed versions; separate repositories cannot merge atomically.
