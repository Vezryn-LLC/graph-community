---
id: release-and-disposition
category: delivery
trigger: "A completed PR or build needs merge or release disposition."
default_skills:
  - source-custody
  - change-aware-verification
---

# Release And Disposition

## Task
A completed PR or build needs merge or release disposition.

## Workflow
1. Check required repository checks and actual scope.
2. Merge and close issues through normal authorized GitHub workflow.
3. Respect real production/destructive action boundaries.
4. Confirm resulting remote or deployed state.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
