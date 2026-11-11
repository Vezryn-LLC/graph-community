---
name: agent-orchestration
description: "Coordinate multiple workers without recreating Codex's scheduler."
---

# Agent Orchestration

## Objective
Coordinate multiple workers without recreating Codex's scheduler.

## Practice
1. Keep one accountable coordinator and allocate nonoverlapping assignments.
2. Give workers original issues, selected playbooks and relevant skills.
3. Dispatch independent work concurrently when capacity permits.
4. Wait on useful worker outcomes, not repeated status polling.
5. Avoid mandatory reviewer agents and redundant investigations.

Guidance only. Do not introduce new Graph services, approval gates or required reviewer loops.
