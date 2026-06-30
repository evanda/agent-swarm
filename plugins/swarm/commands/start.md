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

**First: is this a fresh run or a resume?** A cycle is identified by its issue#,
not by a conversation — so `/swarm:start <issue#>` on an issue that already has
prior state means *continue that cycle*, not start it over. Before routing, check
for prior state:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" status --cycle <issue#>
```

If it reports events (or the issue already carries a `lane:*` label / a
`<!-- swarm:progress -->` checklist comment), this is a **resume**: confirm with
the human — *"cycle N has prior state from M events (lane X, last activity …) —
resume from the frontier, or re-route fresh?"* — and unless they choose re-route,
hand off to the **`resume-cycle`** skill and stop here. Run the fresh flow below
only when there is no prior state (or the human chose to re-route).

Fresh-run flow:

1. If given a description rather than an issue, offer to file an Issue first
   (intake is GitHub Issues). If given an issue number/URL, read it.
2. **Claim before labelling.** Post a machine-readable claim comment on the issue
   *before* applying any `lane:*` labels — async job-pickers watch for `lane:*`
   and will start a parallel run if none is present:
   `🐝 Swarm Orchestrator — interactive run started <!-- swarm:claim mode=interactive -->`
   If an existing claim comment is already present from a different run, surface
   it to the human before proceeding.
3. Run the **`route-issue`** skill → stamp `lane:*` and any `risk:*` labels, with
   a one-paragraph rationale.
4. Execute the chosen lane by **delegating to subagents** (Explorer, Architect↔
   Challenger, Implementer↔Reviewer, Integrator) — you never write code yourself
   and you never hold raw search/diff output.
5. Honor the human gates: Deep-lane specs pause at `spec-review`; anything
   `needs-human` stops and asks.
6. Synthesize condensed results, keep the issue graph current, and ask the Scribe
   to record decisions and file follow-ups.

Report status to the human in plain terms at each lane boundary.
