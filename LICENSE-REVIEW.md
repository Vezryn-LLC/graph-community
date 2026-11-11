# License compatibility review — Apache-2.0 private candidate

The founder selected Apache License 2.0 and confirmed that Vezryn and its AI
coding agents developed Graph Community without known outside contributions.
The unmodified [Apache-2.0 LICENSE](LICENSE) was merged in Community PR #6
and is included in MANIFEST.json. This does not authorize public visibility,
a release or a tag.

The scoped review of the original 28-file candidate found no substantial copied
pstack text or other specific third-party notice-bearing implementation in the
shipped payload. The public pstack source is MIT-licensed, but the private
historical import filenames are unknown and private guidance is not shipped.
No separate NOTICE is indicated by the reviewed contents. Preserve any
applicable upstream copyright and license notices if future versions include
third-party material.

The founder's representation and repository evidence support the release
preparation but do not independently establish legal chain of title, rights to
unknown external material or ownership of third-party trademarks.

## Shipped material and external prerequisites

The package contains authored Python, shell, JSON and generic Markdown plus an
inert CI template. Static Python import analysis permits only bundled modules or
the standard library. No pip dependency, interpreter, standard-library source,
Git/gh/Codex binary, OS library or action source is bundled. No copied third-party
license header has been identified in this source review; absence of a header
is not evidence of original authorship. Maintainers must inspect any copied
snippets/generated inputs and contributor rights, including the native API code.

| Separately installed component | Upstream terms / redistribution consideration |
| --- | --- |
| Python/stdlib | [PSF and component notices](https://docs.python.org/3/license.html). If later bundled, preserve applicable license stack/notices and review component terms; Python modifications may require a change summary. |
| Git | [GPL v2 / per-file terms](https://github.com/git/git/blob/master/COPYING). Bundling Git would require its applicable source/license obligations; calling an independently installed Git does not place its source in this payload. |
| GitHub CLI | [MIT](https://github.com/cli/cli/blob/trunk/LICENSE). Retain notices if distributing its software; no binary is included here. |
| OpenAI Codex CLI | [Apache-2.0](https://github.com/openai/codex/blob/main/LICENSE). Account/service terms, native client availability and model access are separate; no client or account is bundled. |
| Bash/GNU utilities/systemd/launchd/Windows APIs | Host prerequisites only. No host implementation is copied. Bundling installers, images or runtimes would need a fresh per-component inventory. |
| GitHub Actions examples | References to actions are not vendored implementations. Activation must review/pin action revisions, their terms, runner access and billing separately. |

This is a scoped source assessment, not a legal opinion. The private report
retains provenance evidence without shipping private Git history, credentials,
operator logs or personal account data. Final publication still needs an
approved public repository identity and explicit publication authority.

## v0.1.0 disposition

The reviewed candidate includes Apache-2.0, and no specific third-party NOTICE
obligation was identified. Founder first-party development representation was
recorded on Graph #128. No further provenance hunt is required solely because
earlier private pstack import filenames are unknown.

Reassess third-party obligations when source or contributors change. The
confidential reporting route is verified separately in SECURITY.md. No public
release is authorized solely by this license review.
