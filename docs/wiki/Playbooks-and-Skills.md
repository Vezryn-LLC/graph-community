# Playbooks and skills

The engineering library is editable Markdown for native Codex. A playbook gives an assignment its primary execution route; a skill supplies useful supporting practices. These files do not create a second scheduler, model API or permission system.

## Inspect what the coordinator will read

The [library guide](https://github.com/Vezryn-LLC/graph-community/blob/main/docs/LIBRARY.md) is the canonical reference for the inventory, configuration roots, supported paths and precedence. Use its documented `library` command under the intended profile before changing guidance.

Use `python3 -B watcher.py library --explain` when you need to distinguish bundled guidance, a local replacement, a disable marker or a missing/invalid override. This opt-in read-only JSON omits absolute paths and file contents; the ordinary `library` output remains the coordinator's path inventory. Follow the canonical guide for symlink and diagnostic details.

Start from the original issue rather than selecting instructions by label alone. Typical examples are:

- A misleading setup paragraph: [document-and-verify](https://github.com/Vezryn-LLC/graph-community/blob/main/playbooks/document-and-verify.md), supported by [outcome-driven-engineering](https://github.com/Vezryn-LLC/graph-community/blob/main/skills/outcome-driven-engineering/SKILL.md).
- A demonstrated regression: [diagnose-and-repair](https://github.com/Vezryn-LLC/graph-community/blob/main/playbooks/diagnose-and-repair.md), with [change-aware-verification](https://github.com/Vezryn-LLC/graph-community/blob/main/skills/change-aware-verification/SKILL.md) where useful.
- A focused feature: [implement-and-deliver](https://github.com/Vezryn-LLC/graph-community/blob/main/playbooks/implement-and-deliver.md), with checks chosen for the changed behavior.

These are routing examples, not guaranteed model performance or mandatory reviewer stages. The coordinator selects one primary playbook and only relevant skills, then passes their literal instructions and the original task to the worker.

## Make one local change

Suppose your project has a particular verification command. Replace the relevant local playbook with a complete instruction that names the command, when it applies and what its result proves. Keep the scope small; avoid copying the entire library merely to add one sentence.

Use the [documented override procedure](https://github.com/Vezryn-LLC/graph-community/blob/main/docs/LIBRARY.md#overrides-and-disable-markers). A same-path local file replaces the whole default. A `.disabled` marker takes precedence over both default and replacement; deleting a replacement restores the bundled default. A marker cannot erase native, global or project instructions already supplied by Codex.

Inspect effective guidance again and let changes take effect on the next coordinator launch. Drain existing work before changes that need to apply consistently. A service must receive its own environment configuration; changing an unrelated shell does not update it. Source activation remains unavailable in Community, so follow the existing reviewed manual replacement process rather than assuming a library edit installs runtime code.

Propose generally useful improvements through the [contribution process](https://github.com/Vezryn-LLC/graph-community/blob/main/CONTRIBUTING.md). Keep project-specific policy in your own overrides and protect private source and operational data.
