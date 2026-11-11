# Diagnose and Repair

**Use for:** bugs, regressions and production behavior that is demonstrably broken.

1. Locate the observed failure and reproduce it in the smallest useful way.
2. Trace the executing path and find the earliest real defect, rather than patching around symptoms.
3. Repair the cause with a narrow change. Delete now-obsolete workarounds when appropriate.
4. Re-run the failing case and affected integration checks, reusing existing evidence where valid.
5. Publish the fix, update the issue/PR and return to the original objective. Log a separate bug only for a distinct actionable problem.

**Useful skills:** `repair-and-resume`, `change-aware-verification`. Do not turn a one-line fix into an architecture campaign.
