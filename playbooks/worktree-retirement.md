---
id: worktree-retirement
category: delivery
trigger: "A known issue-owned temporary worktree reaches closeout, including a late PR merge."
default_skills:
  - source-custody
---

# Worktree Retirement

The native coordinator performs this closeout after the worker exits. Use Git and
normal issue/session handoff evidence; no cleanup daemon, inventory or sweeper.

## Verify before mutation

1. Read the original claim and latest `Graph retirement pending` handoff. Match
   repository, exact canonical worktree path, branch, task HEAD and worker/session
   identity to native `git worktree list --porcelain`, `git -C <path> rev-parse
   --show-toplevel`, `--git-common-dir`, `HEAD` and `--abbrev-ref HEAD`. Inspect the
   remote identity. For public-safe withheld handoffs, also read the same restricted
   local custody record linked privately to the immutable claim URL/body/digest
   and its retirement continuation. Use that record for exact paths, final HEAD,
   native owner and retention evidence; never infer a path from a public alias or
   publish private values in cleanup comments. Missing/conflicting private evidence
   means preserve. A prefix/name/old timestamp is not ownership. Only the exact
   explicitly disposable task checkout qualifies. Conflicting or missing custody
   means preserve; never touch unrelated, main/default, protected, shared or
   manually maintained branches or the repository's primary checkout.
2. Verify live GitHub PR `state`, `mergedAt`, `headRefOid`, `mergeCommit` and the
   issue's successful delivered outcome. Read links and head/base repository and
   branch identities: a closed-without-merge PR, unrelated merge, closed issue or
   auto-deleted remote branch is insufficient. Open/unmerged, blocked, paused or
   uncertain work stays intact. Do not infer that closing the issue ended a worker.
3. Confirm the owning native worker/session and child processes have exited with
   no planned resumption; inspect session/process state and any known working
   directories as appropriate. Check all active assignments/handoffs for dependent
   or in-flight users of that exact path/branch. No active/current checkout may be
   removed. If inactivity or dependent use cannot be established, preserve and
   name the missing evidence. Do not kill processes to make cleanup possible.
4. Fetch the current target/default branch with native Git. Protect all unique
   committed and uncommitted work. Check `git -C <path> status --porcelain
   --untracked-files=all` **and** `git -C <path> ls-files --others --ignored
   --exclude-standard`; meaningful ignored files count too. Check task HEAD still
   matches the verified PR head and recorded handoff (no post-PR commits). Prove
   integration with `git merge-base --is-ancestor <task-head> <fetched-target>`.
   For a squash merge, matching the complete task tree to the verified merge
   commit (`git diff --exit-code <task-head> <merge-commit> --`) plus proving that
   merge commit is in the fetched target can establish source preservation; if
   trees differ or any unique commits/edits remain unaccounted for, preserve.
   Never assume a push or patch description preserved the actual source.

## Retire or preserve

5. Work from a separate stable checkout/directory. Recheck ownership, branch/HEAD,
   inactivity, dependents and cleanliness immediately before mutation. Use only
   `git worktree remove <exact-path>` without force. If it refuses, stop and preserve
   the reason; do not fall back to `rm -rf`, reset, clean, force or bulk prune.
6. After removal, delete only the same disposable local task branch with
   `git branch -d <exact-branch>` when fully integrated and not checked out anywhere
   else. Check its upstream too: `-d` may use the upstream rather than the default
   branch, so independently prove integration first. If safe deletion refuses
   (e.g. squash ancestry), keep that branch and record why; no forced branch delete.
   Optional remote deletion requires the same ownership/integration proof, no
   other users and repository conventions permitting it. Protect default/protected
   and manually maintained branches; remote cleanup is not required for closeout.
7. Verify actual worktree/branch postconditions. Update the existing handoff to
   `Graph retirement complete` with the final disposition (public-safe for public
   repositories, with exact evidence retained in the same private record), or
   retain pending with one actionable preservation reason and next trigger. The worker never deletes
   the checkout it is still using. On retries, inspect reality first: an already
   absent exact owned path/branch needs no deletion or repeated success comment.

## Completion

Return actual issue/PR outcome, source revision, retired/preserved exact path and
branch, safety evidence and remaining next step. Reconcile known pending closeouts
on meaningful completion/merge/recovery events and coordinator restart, even with
no ready backlog. Do not scan arbitrary old worktrees or perform broad cleanup.
Follow `policies/ENGINEERING.md`; independent review is conditional.
