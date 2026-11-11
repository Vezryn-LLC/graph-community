# Claims, delivery and recovery

Before dispatch, verify eligibility and actual clean repository/HEAD/branch/path.
Use a distinct worktree and branch per independent assignment; never overwrite
user or worker source. Add `status:in-progress`, remove ready and stale blocked
reason labels, and write one timestamped comment beginning `Graph claimed —`.
Record coordinator and `worker/session owner: /native/worker` (or worker pending),
exact repository/worktree/branch/HEAD and dependent users. Update that same claim
when allocation becomes known. Pass the full original issue URL/body/comments
and literal selected guidance to the worker. Do not duplicate a claim on retry.

Workers validate, commit, push and open/update the ordinary PR under repository
conventions. Link complete delivery with `Closes #N`. Incomplete work retains its
remaining acceptance. Finished unmerged work becomes `status:awaiting-merge`.
Required CI/protections still apply; merge when authorized and accepted. On actual
delivery close the issue and clear active/reason labels. Preserve pending source.

For genuine blockers, remove conflicting lifecycle labels, add `status:blocked`,
and leave one `Graph blocker —` note with `Owner:`, `Current blocker:`,
`Next action:`, `Clears when:` and `Auto-resume:` fields. State exact authority or
capability gaps. Reassess on meaningful evidence; don't repeat unchanged notes.
Verify all current dependencies and source gates before restoring ready or
resuming the original assignment. Preserve exact custody and one accountable
owner; do not create competing work. Inspect uncertain writes before retrying.

Watcher exit codes and receipts are diagnostics, never task completion. After an
interruption inspect the existing native session, current GitHub claims/PRs and
preserved source before replay. Native start/stop hook events supply ownership
facts. An unmatched start, lost/truncated history or ambiguous ownership holds
dispatch conservatively; complete stop evidence can clear it. Resume/reconcile
the original owner rather than invent a new claim. The optional exact worker-link
receipt reader is an optimization, not required for desktop-free correctness.

Before worker exit leave one `Graph retirement pending` comment with PR/outcome,
exact repository/path/branch/HEAD, worker identity, retained/disposable status,
dependent users, resumption and next trigger. The coordinator owns cleanup only
after confirmed exit, accepted merge, clean integrated source and no dependents.
Never remove an in-use, dirty, paused, unmerged or uncertain checkout. Verify
postconditions and update the same handoff to `Graph retirement complete`.
Branch deletion or issue closure alone is not evidence of safe disposal.
