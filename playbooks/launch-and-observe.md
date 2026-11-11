---
id: launch-and-observe
category: execution
trigger: "The request is to launch an existing program or check."
default_skills:
  - execution-intent-preservation
  - observable-progress
---

# Launch And Observe

## Task
The request is to launch an existing program or check.

## Workflow
1. Check essential prerequisites and launch promptly.
2. Report LAUNCHED, NOT_LAUNCHED or UNKNOWN from actual evidence.
3. Observe real outcome and diagnose concrete failure.
4. Do not turn launch-only work into an infrastructure campaign.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
