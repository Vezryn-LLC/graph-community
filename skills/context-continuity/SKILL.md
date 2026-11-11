---
name: context-continuity
description: "Keep tasks resumable across context, process and quota changes."
---

# Context Continuity

## Objective
Keep tasks resumable across context, process and quota changes.

## Practice
1. Checkpoint issue/PR IDs, worker ownership, branch/worktree, real progress and next action.
2. Use available native continuation or handoff.
3. Reconcile unknown external effects before repeating them.
4. Avoid duplicate worker claims and full transcript copying.

Guidance only. Do not introduce new Graph services, approval gates or required reviewer loops.
