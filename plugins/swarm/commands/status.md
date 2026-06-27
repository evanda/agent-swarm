---
description: Show the live progress checklist for a swarm cycle (rendered from the run log).
argument-hint: <issue#>
disable-model-invocation: true
---

# /swarm:status

Render the **live progress checklist** for a cycle on demand — what each subagent
is doing, dialectic rounds, gates, PRs, and tokens burned so far.

**Cycle:** `$ARGUMENTS` (the issue number; default: the most recent cycle in the log).

1. If no argument, run `python3 scripts/swarm_log.py cycles` and use the latest.
2. Render: `python3 scripts/swarm_log.py checklist --cycle <issue#>` and show it.
3. If the cycle is complete, offer to produce the full report via the `debrief`
   skill.

This reads the local `.swarm/run-log.jsonl`; the same checklist is mirrored live
into the issue's progress comment by the running swarm (see the `run-log` skill).
