---
id: autonomous-issue-to-pr
category: delivery
trigger: "An authorized GitHub issue must become a real delivered PR."
default_skills:
  - outcome-driven-engineering
  - source-custody
  - change-aware-verification
---

# Autonomous Issue To Pr

## Task
An authorized GitHub issue must become a real delivered PR.

## Workflow
1. Read the complete issue and related PRs.
2. Implement in an independent branch/worktree using normal Codex tools.
3. Verify the real behavior and publish or update a PR.
4. Update issue labels, comments and closure accurately. Independent LLM review is conditional, not routine.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
