# Graph Community v0.1.2 candidate

Unreleased source candidate. No tag, archive, runner activation or release is
published by these changes. Existing v0.1.0 and v0.1.1 artifacts remain immutable.

## Recovery correction

An unresolved retirement handoff with a missing cached ready-label epoch can now
request one native reconciliation when complete bounded comments and label
history prove a ready-label event strictly after the latest pending handoff.
Current ready presence alone is insufficient. Missing, incomplete, malformed or
older chronology preserves the hold and exposes a diagnostic with the next action.
Existing non-null event transitions, native ownership holds, parent-scope holds,
claim/source custody and restart deduplication remain in place. A reconciliation
wake does not retire source, clear unresolved effects or prove an old worker exited.

## Verification and limits

Accounts-free synthetic regressions cover recovery, persisted restart without a
second wake, existing event-ID behavior and chronology/ownership/parent negatives.
The package checker covers payload hashes/modes, the deliberate public allowlist,
public history and local checks. These results establish no new native-platform,
account, service, runner or release qualification.
