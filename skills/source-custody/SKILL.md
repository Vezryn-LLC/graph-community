---
name: source-custody
description: "Protect concurrent Git work using normal Git tooling."
---

# Source Custody

## Objective
Protect concurrent Git work using normal Git tooling.

## Practice
1. Inspect actual branch, HEAD and dirty state before editing.
2. Use distinct branches/worktrees for independent tasks.
3. Never overwrite another worker's changes or discard unique work.
4. Check real GitHub state before retrying uncertain push or PR creation.
5. Keep exact repository/branch/worktree/HEAD and worker/session ownership in the issue claim and closeout handoff. Distinguish disposable task source from shared or manually maintained source.
6. On finished work, hand retirement to the coordinator after worker/process exit using ISSUE_LIFECYCLE.md and the effective worktree-retirement playbook. Never remove an active, dirty, unmerged or resumable checkout; preserve every unique commit/edit and dependent user's source. GitHub remote-branch deletion proves nothing about local safety.

Guidance only. Do not introduce new Graph services, approval gates or required reviewer loops.
