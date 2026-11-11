# Claims, delivery and recovery

Before dispatch, verify eligibility and actual clean repository/HEAD/branch/path.
Use a distinct worktree and branch per independent assignment; never overwrite
user or worker source. Add `status:in-progress`, remove ready and stale blocked
reason labels, and write one timestamped comment beginning
`Graph claimed — YYYY-MM-DD HH:MM:SS PST/PDT (offset)`. Obtain the actual Pacific
time and offset; never claim that a worker started before native start evidence.
Finish actual source allocation before launch. An unallocated `worker pending`
claim is incomplete: finalize that same claim before dispatch, without a duplicate.
Pass the original issue URL and complete requirements/comments or native access,
plus literal selected guidance to the worker.

## Readable future claims

Lead with the assignment summary, truthful stage, repository, actual strategy
(playbook and selected/inherited native model/effort) and useful guidance. Keep
literal `Worker:`, `Branch:` and `Worktree:` prefixes on separate, unbolded lines,
with blank lines between them. Preserve actual values under the visibility rules
below. Put useful execution/source-retention details in a GitHub `<details>`
section with a clear `<summary>`; collapsed content is still public.

Check live repository visibility first. For public or unknown visibility, use a
shareable worker alias/branch and exactly
`Worktree: withheld (private local custody)`. Never publish local paths, common
Git directories, host details, opaque native identifiers, private source/history,
credentials or operational logs in public claims, progress, PRs or handoffs.
Do not disclose these values inside expandable details either.

Retain exact repository, canonical worktree/common Git directory, branch, actual
HEAD, native owner and any public alias, dependent users and retention/resumption
disposition in an existing operator-owned restricted local evidence location
(directory mode 0700 and file mode 0600 on POSIX, equivalent access controls on
other hosts). Link it privately to the single claim URL and immutable body/digest.
Pass exact source values in the native worker assignment. Update the same private
record through interruption, resumption and retirement. Missing/conflicting
custody means preserve and investigate; never invent a path or weaken ownership.
For verified private repositories, the claim may retain exact observed source
values, coordinator/worker ownership, HEAD and dependent users. A public example:

```markdown
Graph claimed — 2026-11-11 03:00:00 PST (-0800)

**Assignment:** Deliver the original bounded issue.

**Stage:** Assigned · worker launch pending

**Strategy:** document-and-verify · inherited configured native model/effort

**Guidance:** outcome-driven-engineering, source-custody

Repository: owner/public-repository

Worker: issue-123-worker (assigned, launch pending)

Branch: work/issue-123

Worktree: withheld (private local custody)

<details>
<summary>Execution details</summary>

Exact source custody is retained privately. Source remains preserved until
verified delivery and post-exit retirement checks. Record actual scope and
resumption constraints here without private operational details.

</details>
```

Apply this layout to future claims only. Preserve historical/bound claim bodies
and digests. After allocation is finalized, use separate progress notes for an
actual native start, implementation progress or pending-to-started transition.
On resumption, verify the existing owner and exact preserved source; retain the
same claim and completed progress rather than issuing a competing claim.

### Existing parser and attribution limits

The bundled watcher recognizes the `Graph claimed —` prefix and fingerprints the
claim body/URL. Its ownership diagnostic recognizes a slash-form worker such as
`Worker: /native/worker`; a public alias or pending owner remains `uncertain_claim`.
A stage label, a native-looking name or a comment does not prove native startup,
liveness or ownership. The watcher does not parse or verify worktree paths, and
Community bundles no exact-worktree attribution/metrics reader. A withheld path,
including when a real path contains whitespace, must not be replaced with a fake
or shortened value to satisfy another reader. If an optional external integration
cannot verify the public-safe representation, leave attribution unknown and
record one bounded private diagnostic. Do not retry by exposing private custody,
import a private integration or invent a receipt. Native reconciliation remains
responsible for verified ownership; this limit adds no new dispatch permission.

## Delivery, blockers and recovery

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
repository/branch, source disposition, dependent users, resumption and next trigger.
For public/unknown visibility retain the literal withheld worktree field and
shareable worker alias; update the same restricted local record with exact paths,
actual final HEAD, native owner/process-exit and all source-retention facts. For
verified private repositories retain exact source/owner values in the handoff.
The coordinator owns cleanup only after confirmed exit, accepted merge, clean
integrated source and no dependents. Use both public and private records for
public-safe handoffs; missing private evidence always preserves source.
Never remove an in-use, dirty, paused, unmerged or uncertain checkout. Verify
postconditions and update the same handoff to `Graph retirement complete`.
Branch deletion or issue closure alone is not evidence of safe disposal.
