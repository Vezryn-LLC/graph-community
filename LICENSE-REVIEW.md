# License and notice review — Apache-2.0

Graph Community is public under the unmodified [Apache-2.0 LICENSE](LICENSE),
included in MANIFEST.json. The owner represented first-party development without
known outside contributions for the original release. This review records source
and notice findings; it does not authorize a new release or tag.

The scoped review of the original 28-file candidate found no substantial copied
pstack text or other specific third-party notice-bearing implementation in the
shipped payload. The public pstack source is MIT-licensed. The original release
did not ship the maintained source guidance; the new additions are reviewed separately below.
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
operator logs or personal account data. The public repository is established;
each new release still requires reviewed source and explicit release authority.

## v0.1.0 disposition

The reviewed candidate includes Apache-2.0, and no specific third-party NOTICE
obligation was identified. The initial release used the owner
first-party development representation and its scoped payload review. That review
does not establish provenance or notice compliance for newly added guidance.

Reassess third-party obligations when source or contributors change. The
confidential reporting route is verified separately in SECURITY.md. No public
release is authorized solely by this license review.

## v0.1.1 guidance additions

The [complete source inventory](docs/GUIDANCE-REVIEW.md) classifies all 31 source
playbooks, 23 skills and seven policies. This payload selects 22 engineering
playbooks and 10 engineering skills, retains three Community policies and adapts
three generic coordinator policies. Creative/product profiles and experimental
planning are excluded. Private source instructions, model IDs, Git ancestry,
research and operational evidence are not exported.

The newly selected text was inspected against retained pstack source and its MIT
license, not just assumed covered by the 28-file review. No substantial copied
pstack passage or other specific notice-bearing external material was identified
in these additions. Generic concepts such as minimal implementation, focused
verification and source custody do not by themselves identify copied expression.
No additional MIT/other notice is indicated by this selected content. If future
changes do include external text, preserve its actual author copyright and full
permission/license notice; Apache-2.0 does not erase upstream obligations.

Attribution for the selected engineering guidance: Vezryn Graph contributors.
Community adaptations retain the generic method and remove private operational
references. Source lineage and comparison evidence are retained privately outside
the payload. This bounded source assessment does not certify legal title or
unknown external inputs and does not extend to excluded creative material.
