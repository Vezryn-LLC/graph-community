# Shared engine and platform contract

```text
explicit enrollment + user-owned generic Markdown
                 |
gh metadata <-- one shared watcher
                 | durable pending source scope + OS ownership lock
                 v
            native codex exec
                 | normal native delegation and GitHub tools
                 v
      isolated workers --> verify --> PR / disposition
                 |
       native lifecycle hook --> private local journal
                 |
       restart --> source/claim/ownership reconciliation
```

There is one coordinator launcher and recovery engine. Linux control uses its
existing user-service CLI; macOS uses an experimental LaunchAgent; Windows uses
an experimental native manual detached runner. Platform adapters own paths,
private state, exclusive/inherited ownership, process identity and control.
No graphical client, private attribution writer or usage collector is required.

The watcher records pending scope before launch. Linux/Mac pass an OS lock to the
coordinator; Windows passes a duplicate exclusive file-object handle through an
explicit inherited handle list. A surviving coordinator retains exclusion.
Partial/lost/unknown journals, unverified native session identity, PID reuse and
ambiguous startup intent remain conservative holds. Stops request graceful drain.
Source cleanup preserves uncertain, active or resumable work. Neither an exit
code, stop event, receipt nor closed issue alone proves product success.

`python3 watcher.py capabilities` returns schema version 1, platform,
per-capability `{available, diagnostic}` objects, PATH prerequisite booleans,
receipt schema version 1, legacy JSONL journal format and qualification status.
Availability means implemented adapter, not authentication, permission, trusted
hooks or host support. Consumers reject unknown schema versions and require
operation-specific evidence. Windows reports manual startup without automatic
startup integration. Native hooks remain unverified; source_update is false on
**all** platforms in this candidate.

The existing receipt version-1 fields and exact live-claim matching remain intact.
Native Windows private reads use owner/DACL and file identity checks; POSIX mode
bits are not Windows ACL proof. No optional writer or invented native identifier
is used to narrow ownership. The fallback can hold until actual matching lifecycle
evidence or normal source reconciliation establishes safety.

State, journals, receipts, enrollment, overrides and streamed logs are private
operational data. They belong in runtime copies, never this pristine source
artifact. The SHA256 manifest covers payload bytes and modes, without old Git
objects, remotes, refs, identities or transcripts. It is a reproducibility check,
not a digital signature, license, rights clearance or supported release.

Source activation has no Community origin or implementation here. Local native
process/runtime records remain separate from Git provenance, and history-free
snapshots report revision unknown. They cannot automatically clear source-gated
blocked work. Future reviewed release origins, signed provenance, migration and
real per-platform workflows require separate qualification.
