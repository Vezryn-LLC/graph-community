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


def explain(root: Path, overrides: Path) -> dict:
    """Explain existing resolution without reading Markdown or disclosing paths."""
    def location(path):
        if path.is_dir():
            return "available"
        return "invalid" if path.exists() or path.is_symlink() else "missing"

    try:
        roots = {"bundled_root": location(root), "override_root": location(overrides)}
        effective = resolve(root, overrides)
        names = set(effective)
        for base in (root, overrides):
            for pattern in PATTERNS:
                names.update(path.relative_to(base).as_posix() for path in base.glob(pattern))
        for pattern in PATTERNS:
            names.update(path.relative_to(overrides).as_posix().removesuffix(".disabled")
                         for path in overrides.glob(pattern + ".disabled"))
        entries = []
        for name in sorted(names):
            local = overrides / name
            marker = overrides / (name + ".disabled")
            diagnostics = []
            if (local.exists() or local.is_symlink()) and not local.is_file():
                diagnostics.append("invalid_override_file")
            if marker.is_symlink() and not marker.exists():
                diagnostics.append("broken_disable_marker")
            if marker.exists():
                provenance = "disabled"
            elif name not in effective:
                provenance = "missing"
            else:
                provenance = "overridden" if local.is_file() else "bundled"
            entries.append({"name": name, "provenance": provenance,
                            "override_symlink": local.is_symlink(), "diagnostics": diagnostics})
        return {"version": 1, **roots, "entries": entries}
    except (OSError, RuntimeError, ValueError):
        # Exception text may contain private absolute paths; keep it local.
        return {"version": 1, "diagnostic": "library_inspection_unavailable",
                "entries": []}


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
