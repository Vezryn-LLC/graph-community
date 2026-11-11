---
id: independent-review
category: quality
trigger: "Specific consequential risk or an explicit request warrants review."
default_skills:
  - independent-engineering-review
  - change-aware-verification
---

# Independent Review

## Task
Specific consequential risk or an explicit request warrants review.

## Workflow
1. Inspect exact source changes and acceptance evidence.
2. Investigate plausible concrete defects, not hypothetical future requirements.
3. Separate material blockers from optional preferences.
4. Return actionable findings and recheck only affected changes.

## Completion
Return the actual deliverable and evidence, or a specific blocker. Follow `policies/ENGINEERING.md`; independent review is conditional. Use native Codex/GitHub tools and existing repository capabilities.
