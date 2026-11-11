---
id: pr-maintenance
category: delivery
trigger: "An existing PR needs focused fixes, rebase or completion."
default_skills:
  - source-custody
  - change-aware-verification
---

# Pr Maintenance

## Task
An existing PR needs focused fixes, rebase or completion.

## Workflow
1. Read the actual remote PR and newest head.
2. Fix material feedback, CI or integration conflicts.
3. Run affected tests and required CI without repeated unchanged reviews.
4. Update PR state and merge under existing repository conventions.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
