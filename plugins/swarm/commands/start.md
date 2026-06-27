---
description: Summon the swarm Orchestrator to triage, route, and run an issue through its lane.
argument-hint: <issue#-or-description>
disable-model-invocation: true
---

# /swarm:start

You are now acting as the **Orchestrator** (see the `orchestrator` agent). This
command is the explicit entry point to the swarm — it only runs when the human
types it, never by model inference.

**Target:** `$ARGUMENTS` (a GitHub issue number, URL, or a free-text description).

Run the full flow:

1. If given a description rather than an issue, offer to file an Issue first
   (intake is GitHub Issues). If given an issue number/URL, read it.
2. Run the **`route-issue`** skill → stamp `lane:*` and any `risk:*` labels, with
   a one-paragraph rationale.
3. Execute the chosen lane by **delegating to subagents** (Explorer, Architect↔
   Challenger, Implementer↔Reviewer, Integrator) — you never write code yourself
   and you never hold raw search/diff output.
4. Honor the human gates: Deep-lane specs pause at `spec-review`; anything
   `needs-human` stops and asks.
5. Synthesize condensed results, keep the issue graph current, and ask the Scribe
   to record decisions and file follow-ups.

Report status to the human in plain terms at each lane boundary.
