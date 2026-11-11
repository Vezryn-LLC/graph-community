---
id: maintain-and-refactor
category: build
trigger: "An issue needs cleanup, maintenance or removal of obsolete code."
default_skills:
  - source-custody
  - change-aware-verification
  - outcome-driven-engineering
---

# Maintain And Refactor

## Task
An issue needs cleanup, maintenance or removal of obsolete code.

## Workflow
1. Define behavior to preserve and real maintenance need.
2. Delete dead code, redundant tests/docs and obsolete compatibility within scope.
3. Avoid unrequested rewrites and protect unrelated work.
4. Run relevant regression and deliver the smaller working change.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
