# Contributing — prepublication process

This private candidate contains the reviewed [Apache-2.0 license](LICENSE),
but the public release and outside contributions have not opened. Any future
outside contribution must carry the appropriate inbound rights. No CLA, DCO
or assignment policy is invented here.

For authorized private changes, start with the original issue and generic
AGENTS.md/policies. Use an isolated branch/worktree, implement the smallest useful
change and verify the affected behavior. Run `python3 -B ci/check.py` on a clean
payload/runtime copy before stateful trials; it verifies the initial manifest.
After intentional edits, a maintainer must regenerate/review the manifest through
the controlled packaging process before claiming a new pristine candidate.

Useful scope: documentation corrections, safe enrollment/recovery regressions,
focused platform tests and bug fixes with concrete reproduction. Avoid company
source, curated private guidance, UI/assets, personal data, logs, tokens, account
state, generated runtime files and imported Git history. Add no telemetry,
commercial licensing, unattended publication or source activation under this
preflight's authority.

PRs should explain the trigger, final behavior, commands/results and remaining
limits. Distinguish Linux-hosted simulations, local primitive execution and real
native service/client/account observations. Routine changes do not require a
second model review. Material security/authorization or hard-to-validate changes
need targeted review of the actual risk. Report vulnerabilities privately as in
SECURITY.md, not through a public issue.

## Preparing v0.1

Use the existing independent Community history and reviewed source allowlist.
Do not reimport the private upstream history. Keep qualification transcripts,
account state and private source lineage outside this repository.

1. Integrate only accepted runtime changes, regenerate the existing manifest and
   run `python3 -B ci/check.py` on the exact clean candidate. Record the candidate
   commit and manifest digest in the release notes prepared for review.
2. Reconcile real Linux, macOS arm64 and native Windows 11 x64 qualification with
   that candidate. Reuse valid unchanged evidence; verify affected boundaries
   when source changes. All three are required before launch.
3. The founder has represented that Vezryn and its coding agents produced the
   release source without known outside developer contributions; a scoped review
   found no specific upstream notice obligations. The Apache-2.0 license is
   included. Verify confidential reporting, final repository identity and
   explicit publication authority before making a release.
4. Prepare a short v0.1.0 release description: what Graph does, prerequisites,
   tested platforms/client versions and explicit limits (manual Windows startup,
   no source updater). Review exact source and documentation once more.
5. Only after explicit publication authorization, create the `v0.1.0` tag and
   GitHub release from that reviewed commit and make the authorized visibility
   change. These are future owner actions, not instructions to publish now.

Use `v0.1.0` for the first approved release. Subsequent compatible fixes can use
`v0.1.1`; document breaking behavior explicitly before increasing the minor
version. No version service, package registry, release workflow or signing
infrastructure is required by this preparation.
