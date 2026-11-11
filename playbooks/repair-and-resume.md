---
id: repair-and-resume
category: coordination
trigger: "Recoverable issue work was interrupted."
default_skills:
  - repair-and-resume
  - change-aware-verification
  - observable-progress
---

# Repair And Resume

## Task
Recoverable issue work was interrupted.

## Workflow
1. Identify last confirmed work and the concrete failure.
2. Repair with focused verification.
3. Reconcile ambiguous external effects before repeating operations.
4. Resume original issue rather than initiating a broad repair campaign.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
