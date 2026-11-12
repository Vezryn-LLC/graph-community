# Contributing

Graph Community is public under [Apache-2.0](LICENSE). Contributors must have
rights to their changes and preserve applicable copyright/license notices.
No CLA, DCO or assignment policy is implied. Read [AGENTS.md](AGENTS.md), the
[engineering policy](policies/ENGINEERING.md) and [library guide](docs/LIBRARY.md).

Start from the original issue and an isolated branch/worktree. Implement the
smallest useful change, reuse existing coverage and verify affected behavior.
Routine changes need no independent model reviewer. Material authorization,
credential, irreversible or hard-to-validate risks require targeted review.
Report actual versus simulated evidence and remaining limitations in the PR.
Security vulnerabilities go privately to the route in [SECURITY.md](SECURITY.md).

Before proposing payload changes, deliberately update the reviewed positive
allowlist in `ci/check.py` only for approved source paths. Regenerate
`MANIFEST.json` file hashes/modes after intentional edits; it covers every payload
file except itself. Run `python3 -B ci/check.py` on the exact clean source.
The checker runs local guidance regressions, document links and primitive smoke;
it does not authenticate, start a service or call a model.

Do not add private source, personal data, credentials, operational logs/state,
product profiles or unrelated history. Reuse this repository's independent Git
history. The [source/notice inventory](docs/GUIDANCE-REVIEW.md) and
[license review](LICENSE-REVIEW.md) explain the newly shipped guidance. Reassess
provenance and include actual upstream notices for any new external material.

## Small ways to start

Check [open issues](https://github.com/Vezryn-LLC/graph-community/issues) and
[PRs](https://github.com/Vezryn-LLC/graph-community/pulls) before picking a slice.
If no suitable beginner issue exists, propose a focused documentation PR or
ask about the scope first. These small opportunities build on current source:

- **Show the first local success.** Add a short, redacted example of the
  Quickstart's accounts-free check output, explaining what a pass proves and
  what still needs native-host/account qualification. Capture actual output;
  do not fabricate a Codex delivery transcript.
- **Make Windows prerequisites easier to inspect.** Add a concise PowerShell
  command for checking the required native Python/Git/GitHub/Codex executables
  against the existing PATH rules. Keep WSL, batch shims and untested host
  behavior distinct from native Windows qualification.
- **Catch broken section links locally.** Extend `ci/check.py`'s documentation
  link check to validate local Markdown section fragments, with small passing
  and missing-anchor fixtures. It currently checks destination files, not
  section anchors; keep this check accounts-free and dependency-free.

These are contribution ideas, not assigned or automatically ready work. A
deferred runtime issue is not a beginner task merely because it is open.
Maintainers control `good first issue`, `help wanted` and Graph lifecycle labels.

## Open an issue

You do not need to know Graph's internal labels or run Codex to participate.

1. Check the [existing issues](https://github.com/Vezryn-LLC/graph-community/issues)
   and [pull requests](https://github.com/Vezryn-LLC/graph-community/pulls)
   to avoid duplicates.
2. Choose **New issue** from the Issues tab, or
   [open a new issue](https://github.com/Vezryn-LLC/graph-community/issues/new).
3. Write a short, descriptive title and explain the problem or improvement.
   Submit when it has enough context to understand the request.

For a **bug report**, include:

- Expected and actual behavior.
- Steps/commands to reproduce the bug, ideally in a disposable repository.
- Graph Community version/commit, OS, Python and native Codex CLI versions.
- Relevant *redacted* errors or logs and whether the problem repeats.

For a **feature request**, explain the problem, current workflow, desired
outcome and why it would help. Concrete examples are welcome; submitting
a request is not a promise to implement or release it.

**Security vulnerabilities:** Do not post exploit details, credentials
or private repository contents in public. Use the confidential route in
[SECURITY.md](SECURITY.md).

**Issue labels are maintainer-controlled.** Opening an issue does not
enqueue an AI agent. Authorized maintainers decide whether and when to mark
an eligible issue `status:ready` after assessing scope, dependencies and
permissions. Contributors do not need to assign Graph-specific labels.

## Submit a pull request

Small documentation fixes can go straight to a PR. For a substantial behavior
change, please check or open an issue first so you don't duplicate work.

1. **Fork** [Graph Community](https://github.com/Vezryn-LLC/graph-community)
   using GitHub's Fork button if you do not have write access. Clone your fork,
   or use GitHub's web editor for simple documentation updates.
2. **Create a branch** from current `main`, such as
   `fix/clearer-startup-message`. Keep each PR focused on one change.
3. **Make and verify the change.** Follow the engineering guidance above.
   Update affected docs/tests. Refresh `MANIFEST.json` for any payload edits;
   update the approved positive file allowlist in `ci/check.py` when adding
   new paths. Run `python3 -B ci/check.py` and relevant focused checks.
   State anything you could not verify.
4. **Push your branch.** On GitHub, select **Contribute → Open pull request**
   (or open the Pull requests tab). Confirm that the base is
   `Vezryn-LLC/graph-community:main` and the comparison is your branch.
   Review the diff before submitting.
5. **Describe your PR**: problem, changed behavior/files, how you tested,
   any platform limitations and the related issue. Use `Fixes #123` only
   when merging would genuinely resolve that issue. Draft PRs are welcome
   for unfinished contributions.
6. **Respond to feedback** in the PR conversation. Maintainers decide when
   a change is merged; merging does not automatically publish a release.

Please keep user data, credentials, private histories and sensitive logs out
of public issues and PRs.

## Release preparation

Keep existing releases and their artifacts immutable. A merged PR is not release
authorization. Record exact source/manifest identity, changed behavior and applicable evidence before
an owner-authorized tag/release. Source activation remains unavailable.

Reuse valid native platform evidence when contracts are unchanged; do not replay
qualification just for Markdown additions. Recheck an affected boundary when a
runtime change invalidates earlier evidence. Do not enable paid CI, change
repository visibility, deploy or grant account access without that action's
specific authority. No package registry or new release engine is needed.
