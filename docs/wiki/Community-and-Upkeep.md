# Community and documentation upkeep

Start with a small correction, reproducible bug or focused improvement. Check [open issues](https://github.com/Vezryn-LLC/graph-community/issues) and [existing PRs](https://github.com/Vezryn-LLC/graph-community/pulls), then follow [CONTRIBUTING.md](https://github.com/Vezryn-LLC/graph-community/blob/main/CONTRIBUTING.md). You do not need Codex, maintainer labels or a full runtime installation to improve documentation.

For security concerns, use the confidential route in [SECURITY.md](https://github.com/Vezryn-LLC/graph-community/blob/main/SECURITY.md). Never put an undisclosed exploit, credential or private repository content in a public issue or Wiki edit.

## Who maintains what

Repository maintainers own the Wiki and its release-time accuracy. Contributors suggest changes through the existing issue/PR workflow. Wiki editing remains restricted to repository writers; the tutorials do not grant access or expand that policy.

| Material | Maintained source |
| --- | --- |
| Installation, commands and native prerequisites | [QUICKSTART.md](https://github.com/Vezryn-LLC/graph-community/blob/main/QUICKSTART.md) and [PLATFORMS.md](https://github.com/Vezryn-LLC/graph-community/blob/main/PLATFORMS.md) |
| Runtime/recovery behavior and architecture | [ARCHITECTURE.md](https://github.com/Vezryn-LLC/graph-community/blob/main/ARCHITECTURE.md) and the current public code |
| Security reporting and boundaries | [SECURITY.md](https://github.com/Vezryn-LLC/graph-community/blob/main/SECURITY.md) |
| Engineering guidance and customization | [docs/LIBRARY.md](https://github.com/Vezryn-LLC/graph-community/blob/main/docs/LIBRARY.md), public policies/playbooks/skills |
| Task-oriented tutorials and navigation | [Wiki Markdown sources](https://github.com/Vezryn-LLC/graph-community/tree/main/docs/wiki) and the published Wiki |

## Make maintenance part of the change

When an engineering PR changes user-visible commands, installation, platform behavior, configuration, playbooks, troubleshooting or security guidance, update the affected source-controlled docs in that same PR, or state why no documentation change is needed. This is a normal engineering habit, not another approval stage or generic test matrix.

On a real Community release, the release maintainer reads the affected Wiki tutorials, Home's version statement, platform/support claims and links. Publish a small Wiki correction only where the release changes the guidance. Inspect the actual remote pages and navigation after publishing; do not infer that merging a repository PR updated the separate Wiki Git repository.

For tutorial edits, change the Markdown under `docs/wiki/` through a focused PR, then publish those reviewed pages to the Wiki repository using GitHub's supported editing or Git path. Before copying a page, read the current Wiki version and preserve community/maintainer changes; reconcile them rather than overwriting unknown work. Keep the root reference documents authoritative and avoid copied command tables that can drift.

Use existing release work, issues and bug reports to surface confirmed drift. No constant AI scan, new documentation service or release tag change is needed for a prose correction. Contributors can open an issue with the stale page URL, the relevant current reference and a proposed correction.
