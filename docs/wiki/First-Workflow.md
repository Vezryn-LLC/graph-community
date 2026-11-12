# Your first workflow

Use a repository you control, with no production data and no existing active assignment. This is an illustrative walkthrough; it is not a transcript of a verified run and does not promise that every task will finish successfully.

## 1. Start without side effects

Complete the [Quickstart's acquisition-to-local-check path](https://github.com/Vezryn-LLC/graph-community/blob/main/QUICKSTART.md#acquire-source-and-make-a-fresh-runtime-copy) in a separate runtime copy. Read the output's scope. Passing it establishes local payload and primitive checks, not account authentication or native lifecycle delivery.

Before a real trial, follow the Quickstart's prerequisites, lifecycle-label setup and platform-specific instructions. Authenticate your own GitHub and native Codex tools interactively and qualify trusted hooks on the intended host. Graph does not grant permissions or perform that sign-in for you.

## 2. Write one bounded issue

The unreleased current-source path includes the [local first-issue exercise](https://github.com/Vezryn-LLC/graph-community/tree/main/examples/first-issue) before account setup. It includes a tiny greeting CLI, an exact issue template and focused tests: the default greeting passes, while the requested `--uppercase` test deliberately starts red. Its one-page walkthrough owns the expected fixture outputs and optional disposable-repository journey; these are not an authenticated Graph transcript.

For an optional real trial, commit the unchanged fixture to an authorized disposable private test repository and use its `ISSUE.md` as one bounded request. Do not enroll production repositories. Describe the expected behavior and finite validation; avoid a broad request such as “improve the whole product.”

Check existing issues, PRs and worker ownership first. An authorized maintainer marks the issue `status:ready` only after its dependencies and scope are actionable. [Enrollment and readiness](https://github.com/Vezryn-LLC/graph-community/wiki/Enrollment-and-Readiness) explains why opening an issue is not enough.

## 3. Enroll, inspect, then run deliberately

Use the [canonical foreground-trial commands](https://github.com/Vezryn-LLC/graph-community/blob/main/QUICKSTART.md#one-real-issue-only-after-native-hostaccount-authorization) for the selected platform. Confirm the enrolled repository list and effective library before invoking the watcher. **`watch --once` is live:** it can read GitHub and launch a real coordinator. It is not a dry-run.

Do not start a second watcher to accelerate a trial. Keep the same source, profile and native-host configuration throughout.

## 4. Follow the actual GitHub record

A selected issue should acquire a timestamped claim and `status:in-progress`, tied to one worker and isolated source. The worker implements and validates the original request, then creates an ordinary PR or records a concrete blocker. Review the diff, checks and evidence through the project's normal workflow.

A PR waiting for disposition is distinct from accepted delivery. A merged source change may still have operational acceptance left. Use the issue's recorded outcome and remaining gates; do not infer success from a process exit or a green local check.

## 5. Stop and retain evidence

Use the [documented platform stop/drain procedure](https://github.com/Vezryn-LLC/graph-community/blob/main/PLATFORMS.md). Let surviving workers finish or preserve their resumable source and claims. Do not kill workers, delete state or remove a worktree just to make a restart look clean. [Troubleshooting and recovery](https://github.com/Vezryn-LLC/graph-community/wiki/Troubleshooting-and-Recovery) covers what to inspect when ownership is uncertain.
