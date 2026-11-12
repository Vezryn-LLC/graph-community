# Graph Community v0.1.2 candidate

Unreleased source candidate, prepared after published **v0.1.1**. This document
is the changelog for the candidate; it does not announce a release. No v0.1.2
tag or download URL exists as part of this preparation. v0.1.0 and v0.1.1 tags,
notes and assets remain immutable.

## Additions since v0.1.1

- Accounts-free `doctor` reports local prerequisites without executing discovered
  tools, creating state, authenticating or dispatching work ([PR #16](https://github.com/Vezryn-LLC/graph-community/pull/16)).
- `library --explain` shows effective guidance provenance without changing routing
  ([PR #17](https://github.com/Vezryn-LLC/graph-community/pull/17)).
- Read-only `queue` inspects current ready-label candidates through authenticated
  GitHub reads, without enrolling repositories or launching a coordinator. Readiness
  alone is not selection or permission ([PR #22](https://github.com/Vezryn-LLC/graph-community/pull/22)).
- A tiny local first-issue exercise has a passing baseline and an intentionally
  failing `--uppercase` acceptance case; it needs no accounts or Graph dispatch
  ([PR #28](https://github.com/Vezryn-LLC/graph-community/pull/28)).
- `version --json` reports local Git/manifest identity, while `status --json`
  reports bounded local monitor facts with explicit unknown/stale values. Neither
  establishes running-source identity or delivery
  ([PR #33](https://github.com/Vezryn-LLC/graph-community/pull/33),
  [PR #34](https://github.com/Vezryn-LLC/graph-community/pull/34)).
- `repo check` separately reads repository metadata and lifecycle labels, reporting
  missing labels versus unavailable reads without changing enrollment or labels
  ([PR #35](https://github.com/Vezryn-LLC/graph-community/pull/35)).
- Platform entrypoints forward doctor, library provenance and queue diagnostics
  ([PR #36](https://github.com/Vezryn-LLC/graph-community/pull/36)).
- Deterministic source-only archive construction reuses the positive payload
  allowlist, checks hashes/modes and a clean extraction, and emits SHA-256 receipts
  ([PR #30](https://github.com/Vezryn-LLC/graph-community/pull/30)).
- README/contributor onboarding, reviewed Wiki tutorials and version-correct source
  acquisition now distinguish published v0.1.1 from newer source
  ([PR #10](https://github.com/Vezryn-LLC/graph-community/pull/10),
  [PR #12](https://github.com/Vezryn-LLC/graph-community/pull/12),
  [PR #13](https://github.com/Vezryn-LLC/graph-community/pull/13),
  [PR #37](https://github.com/Vezryn-LLC/graph-community/pull/37)).

## Behavior changes and recovery

- Enrollment edits serialize before reading configuration. Competing add/revoke
  operations fail with a retry message instead of losing updates; a private
  config-side lock remains. Revocation does not terminate surviving workers
  ([PR #31](https://github.com/Vezryn-LLC/graph-community/pull/31)).
- Linux service installation binds its resolved config/state/library profile.
  Mismatched controls and old units with unverifiable profiles refuse operation;
  reconcile the original watcher while idle before reinstalling. Failed reloads
  roll back owned files and report an unverified manager when rollback reload fails
  ([PR #32](https://github.com/Vezryn-LLC/graph-community/pull/32)).
- An unresolved retirement handoff with a missing cached ready-label epoch can
  request one reconciliation when complete bounded comments and label history
  prove a ready-label event strictly after the latest pending handoff. Current
  readiness alone is insufficient. Incomplete, malformed or older chronology
  preserves the hold and diagnostic. Existing event-ID transitions, native
  ownership, parent-scope holds and restart deduplication remain. A wake does not
  retire source or prove an old worker exited
  ([PR #38](https://github.com/Vezryn-LLC/graph-community/pull/38)).

## Compatibility and acquisition

Python 3.11+ and Git remain required; there are no pip dependencies. Linux's Bash
entrypoint additionally needs GNU readlink, systemd user services and a qualifying
`/usr/bin/python3`. Foreground Python checks need no service manager. Native Codex,
GitHub authentication, delegated-worker capability and trusted hooks remain
operator prerequisites for actual work. Environment variables retain the
`VEZRYN_GRAPH_*` prefix. See [Quickstart](QUICKSTART.md) and [platform limits](PLATFORMS.md).

The Quickstart's **published v0.1.1** filenames, checksum and tagged instructions
continue to describe v0.1.1 only. Its separately pinned current-source example is
an earlier reproducible unreleased snapshot. Use the candidate procedure below
for this PR's complete candidate, rather than substituting a nonexistent
`releases/download/v0.1.2/` URL. A release-note filename is not a machine-readable
version declaration: `version` still reports release version as unknown.

## Reproduce this source candidate

Use the exact accepted candidate commit recorded in the preparation PR's evidence.
In a fresh clone, inspect that commit and its diff from the accepted baseline,
then detach it. Keep the output directory outside the pristine source checkout.
These Linux/macOS shell commands create local files only:

```sh
git clone https://github.com/Vezryn-LLC/graph-community.git source
cd source
git checkout --detach <candidate-commit>
git rev-parse HEAD
python3 -B ci/check.py
mkdir ../candidate
python3 -B ci/archive.py ../candidate/graph-community-v0.1.2-candidate.tar > ../candidate/archive-check.log
python3 -B ci/archive.py ../candidate/rebuild.tar > ../candidate/rebuild-check.log
cmp ../candidate/graph-community-v0.1.2-candidate.tar ../candidate/rebuild.tar
python3 -c "from pathlib import Path; import hashlib; p=Path('../candidate/graph-community-v0.1.2-candidate.tar'); print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name)" > ../candidate/SHA256SUMS
python3 -c "import shutil; shutil.unpack_archive('../candidate/graph-community-v0.1.2-candidate.tar','../candidate/runtime')"
cd ../candidate/runtime
python3 -B ci/check.py
python3 -B watcher.py doctor --json
python3 -B graph_update.py version --json
```

Replace `<candidate-commit>` with the full source SHA; do not type the angle
brackets into the shell. The candidate archive is an uncompressed **`.tar`**, with
files directly at its root, unlike the historical v0.1.1 `.tar.gz` wrapper.
`archive-check.log` ends with the archive/manifest digests and extraction result.
Retain it alongside SHA256SUMS and the exact source SHA; archives are not committed
or uploaded by this procedure. Existing output paths fail rather than overwrite.
The second archive must have identical bytes despite its different filename.

The builder compares every archive byte and mode to the validated source before
extracting, including `.codex` dotfiles and executable `bin/graph`, and runs the
existing accounts-free checker on a fresh extraction. A separate fresh runtime
check above is safe to run without accounts. Keep later state outside pristine
source. The allowlist omits `.git`, runtime enrollment/journals, secrets, private
product guidance and historical repository artifacts. Hashes detect mismatch;
they are not publisher signatures, rights grants or proof of native hooks.

## Verification and known limits

Preparation evidence in the PR records exact source, archive and manifest hashes,
Linux/Python identity, reproducible archive comparison and source/extracted checks.
The checker compiles/imports Python, validates payload completeness, modes, public
history (source only), local documentation links, focused regressions and primitive
smoke. Recovery, service-profile, enrollment and entrypoint tests include synthetic
or isolated process/service fixtures; those are not native account trials.

No new native macOS or Windows installation/control trial, authenticated GitHub
first issue-to-worker-to-PR journey, trusted client-hook qualification, updater,
automatic service activation or real external-user acceptance is performed for
this candidate. Existing bounded Linux, macOS arm64 and Windows 11 x64 witnesses
in [PLATFORMS.md](PLATFORMS.md) remain historical evidence for their reviewed
source/client combinations, not qualification of every later package. Linux and
Windows reboot recovery remain unqualified; Windows startup is manual. Source
activation and automatic updates remain unavailable on every platform.

Promotion is separate: a release owner must review this exact candidate's source,
receipts and any affected native scenarios, then separately authorize any tag,
release assets or announcement. This preparation neither changes an installed
runtime nor starts/enables a service. The Wiki was inspected for version/link
consistency; its historical v0.1.1 statement and links to current documentation
remain truthful. A source PR does not republish the Wiki.
