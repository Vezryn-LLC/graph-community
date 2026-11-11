---
id: context-handoff
category: coordination
trigger: "Active work needs a coordinator or worker context handoff."
default_skills:
  - context-continuity
  - observable-progress
---

# Context Handoff

## Task
Active work needs a coordinator or worker context handoff.

## Workflow
1. Checkpoint issue IDs, worker/session IDs, branches, PRs, finished work and next actions.
2. Use native Codex continuation or successor support where available.
3. Confirm successor ownership before retiring the predecessor.
4. Never duplicate active work or replay an uncertain external write.

Keep exact ownership and pending retirement handoffs in continuity context. Paused or resumable source stays intact. On recovery/restart, reconcile only known completed/merged candidates under ISSUE_LIFECYCLE.md and the effective worktree-retirement playbook; do not rediscover candidates by sweeping old worktrees.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
