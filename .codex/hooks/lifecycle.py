#!/usr/bin/env python3
"""Advisory Graph hooks: inject guidance and record native agent lifecycle facts."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from library import instructions, resolve
from graph_platform import paths, private_directory, check_private, platform_name, file_target, native_journal


def override_root():
    """Match the watcher configuration without loading its runtime."""
    config, _ = paths()
    return Path(os.environ.get(
        "VEZRYN_GRAPH_LIBRARY", str(config.parent / "library"))).expanduser()

GITHUB_LINK = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/[1-9][0-9]*"
)


def record(event, payload):
    """Append only minimal identifiers; never store full prompts, tool responses or secrets."""
    try:
        journal = native_journal(ROOT)
        private_directory(journal.parent)
        entry = {"event": event, "at": datetime.now(timezone.utc).isoformat()}
        entry.update({k: v[:200] for k, v in payload.items()
                      if isinstance(v, str) and v})
        for k in ("issues", "prs"):
            if isinstance(payload.get(k), list):
                entry[k] = payload[k][:12]
        file_target(journal)
        if journal.exists() or journal.is_symlink():
            check_private(journal)
        fd = os.open(journal,
                     os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            os.write(fd, (json.dumps(entry, separators=(",", ":")) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
    except (OSError, RuntimeError):
        pass  # Observation must never gate an engineering worker.


def context(kind, message):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": kind, "additionalContext": message,
    }}))


def unpack_response(response):
    """Accept the v1 agent_id or v2 task_name when Codex supplies one."""
    if isinstance(response, dict):
        for k in ("agent_id", "task_name"):
            if isinstance(response.get(k), str) and response[k]:
                return response[k]
        for k in ("content", "output", "result", "text"):
            if k in response:
                found = unpack_response(response[k])
                if found:
                    return found
    elif isinstance(response, list):
        for item in response[:6]:
            found = unpack_response(item)
            if found:
                return found
    elif isinstance(response, str):
        try:
            decoded = json.loads(response)
            if decoded != response:
                return unpack_response(decoded)
        except ValueError:
            pass
        match = re.search(r'"(?:agent_id|task_name)"\s*:\s*"([^"]+)"', response)
        if match:
            return match.group(1)
    return ""


def assignment(event):
    if not str(event.get("tool_name", "")).endswith("spawn_agent"):
        return
    args = event.get("tool_input", {})
    if not isinstance(args, dict):
        args = {}
    parts = [args.get("message", "")]
    if isinstance(args.get("items"), list):
        parts.extend(x.get("text", "") for x in args["items"] if isinstance(x, dict))
    prompt = "\n".join(x for x in parts if isinstance(x, str))
    urls = list(dict.fromkeys(m.group(0) for m in GITHUB_LINK.finditer(prompt)))
    result = {
        "session_id": event.get("session_id", ""),
        "turn_id": event.get("turn_id", ""),
        "agent_id": unpack_response(event.get("tool_response")),
        "name": args.get("task_name", "") if isinstance(args.get("task_name"), str) else "",
        "model": args.get("model", "") if isinstance(args.get("model"), str) else "",
        "effort": args.get("reasoning_effort", "") if isinstance(args.get("reasoning_effort"), str) else "",
        "source_issue": next((u for u in urls if "/issues/" in u), ""),
        "issues": [u for u in urls if "/issues/" in u],
        "prs": [u for u in urls if "/pull/" in u],
    }
    if result["agent_id"] or result["name"]:
        record("spawned", result)
        # No optional private attribution writer is bundled. The generic
        # recovery journal and exact-claim receipt reader remain independent.


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            event = {}
    except (ValueError, UnicodeError):
        event = {}
    kind = event.get("hook_event_name")
    if kind == "SessionStart":
        context(kind,
            "For a Graph coordinator session, read AGENTS.md and the required "
            "effective coordinator policies, qualify enrolled ready issues and "
            "delegate original tasks with selected literal guidance. If this is "
            "an explicitly assigned worker session, honor that assignment and "
            "delivery role instead; do not start another backlog campaign. "
            "Creative routing applies only to creative objectives. Native/global "
            "standing instructions remain independently applicable.\n\n"
            + instructions(ROOT, override_root())
        )
    elif kind == "SubagentStart":
        record("subagent_started", {k: event.get(k) for k in
            ("session_id", "turn_id", "agent_id", "agent_type", "model", "cwd")})
        path = resolve(ROOT, override_root()).get("policies/ENGINEERING.md")
        principles = ("Effective Graph engineering guidance (" + str(path) + "):\n"
                      + path.read_text(encoding="utf-8")) if path else (
            "Graph library ENGINEERING.md is disabled or unavailable; no bundled "
            "fallback was loaded.")
        context(kind,
            "Graph Community worker: honor the original GitHub task and coordinator's "
            "selected playbook/skills. Verify actual behavior. Independent LLM review "
            "is conditional, not automatic. Do not start a coordinator backlog "
            "campaign or load unselected creative skills. Native/global AGENTS.md "
            "and higher-priority standing instructions still apply independently; "
            "a Graph .disabled marker cannot erase them. Use effective library "
            "sources for any further guidance selection.\n\n" + principles)
    elif kind == "SubagentStop":
        record("subagent_stopped", {k: event.get(k) for k in
            ("session_id", "turn_id", "agent_id", "agent_type")})
        print("{}")
    elif kind == "PostToolUse":
        diagnostic = assignment(event)
        if diagnostic:
            context(kind, diagnostic)
        else:
            print("{}")
    else:
        print("{}")


if __name__ == "__main__":
    main()
