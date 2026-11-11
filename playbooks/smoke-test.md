---
id: smoke-test
category: execution
trigger: "The task calls for a quick representative functional check."
default_skills:
  - change-aware-verification
  - observable-progress
---

# Smoke Test

## Task
The task calls for a quick representative functional check.

## Workflow
1. Choose one scenario that exercises the intended artifact.
2. Run it and retain actual output/error details.
3. Report PASS, FAIL or UNKNOWN accurately.
4. Expand verification only for observed or material risks.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
