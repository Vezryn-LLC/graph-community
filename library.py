"""Resolve Markdown guidance paths; Codex owns selection and execution."""
import json
from pathlib import Path

PATTERNS = ("policies/*.md", "playbooks/*.md", "skills/*/SKILL.md")


def resolve(root: Path, overrides: Path) -> dict[str, Path]:
    """User file replaces default; adjacent .disabled marker wins over both."""
    entries = {}
    for pattern in PATTERNS:
        for base in (root, overrides):
            for path in base.glob(pattern):
                if path.is_file():
                    entries[path.relative_to(base).as_posix()] = path.resolve()
    return {
        name: path for name, path in sorted(entries.items())
        if not (overrides / (name + ".disabled")).exists()
    }


def instructions(root: Path, overrides: Path) -> str:
    entries = resolve(root, overrides)
    lines = [
        "Effective Markdown library (logical name => file path):",
        "This inventory is authoritative for guidance references, including references",
        "inside AGENTS.md and the Markdown. Read required coordinator policies before",
        "coordinator work; domain policies such as CREATIVE_ROUTING apply only to",
        "relevant objectives. Use these effective paths, not bundled fallbacks, before",
        "assigning work. Select one available playbook and only useful available skills;",
        "read their actual files and pass their literal contents to the native worker.",
        "A missing logical name is disabled or unavailable: do not load its bundled",
        "counterpart or substitute a disabled default. Explain a material missing policy",
        "or playbook and defer work if you cannot safely proceed. Local target-repository",
        "instructions and the user's authorization still apply. This library grants no",
        "additional permissions. Native/global AGENTS.md remains independently applicable:",
        "a disabled marker cannot remove instructions already supplied by Codex.",
        "Paths are JSON strings, not shell commands.",
    ]
    lines.extend(f"- {name} => {json.dumps(str(path))}" for name, path in entries.items())
    return "\n".join(lines) + "\n"
