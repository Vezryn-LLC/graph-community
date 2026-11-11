---
id: pause-and-recover
category: coordination
trigger: "Quota interruption, user stop or worker failure requires continuity."
default_skills:
  - context-continuity
  - observable-progress
  - repair-and-resume
---

# Pause And Recover

## Task
Quota interruption, user stop or worker failure requires continuity.

## Workflow
1. Preserve worktrees and known completed effects.
2. Distinguish confirmed quota pause from uncertain in-flight operations.
3. Resume native work after verified allowance recovery when supported.
4. Do not disrupt unrelated healthy workers or blindly replay uncertain actions.

Keep exact ownership and pending retirement handoffs in continuity context. Paused or resumable source stays intact. On recovery/restart, reconcile only known completed/merged candidates under ISSUE_LIFECYCLE.md and the effective worktree-retirement playbook; do not rediscover candidates by sweeping old worktrees.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
