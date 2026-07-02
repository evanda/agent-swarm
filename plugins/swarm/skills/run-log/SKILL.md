---
name: run-log
description: The instrumentation contract — the event schema every swarm agent emits to .swarm/run-log.jsonl, and how the live progress checklist is mirrored into a GitHub issue comment. Invoked by all swarm agents (esp. the Scribe). Not for general use.
user-invocable: false
---

# run-log

Makes an otherwise-opaque, token-heavy swarm run **legible**. Every agent emits
structured events; the human-facing views (live checklist, debrief) are *rendered
from those events* so they never drift from what actually happened. This is the
instrumentation principle (#7) made concrete.

## Emit events (every agent, at every boundary)

Use the helper — do not hand-write JSONL. It **ships inside the plugin**, so it is
present at runtime in any activated repo (no agent-swarm clone needed); always
invoke it via `${CLAUDE_PLUGIN_ROOT}`:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" log --cycle <issue#> \
    --event <type> [--agent ..] [--lane ..] [--task ..] [--detail "..."] \
    [--round N] [--tokens N] [--status pending|in_progress|done|blocked|crashed] [--data '{...}']
```

`crashed` is a distinct status from `blocked`: use it when an agent's completion is
ambiguous — interrupted mid-write, process restart, dropped connection — so a
partial artifact is never recorded (or rendered) as indistinguishable from a
clean `done`. Emit it on the `agent_returned` event once the interruption is
confirmed; an unconfirmed interruption should not be logged as `done` at all.

The log is written to the **working repo's** `.swarm/run-log.jsonl` (override with
`--file`), kept relative to the repo you're operating in — not the plugin cache.

### Event vocabulary (closed set)

| event | when | who |
|---|---|---|
| `cycle_started` | a cycle begins (one issue) | Orchestrator |
| `lane_routed` | route-issue picked a lane (+risk) | Orchestrator |
| `agent_dispatched` | a subagent is spawned for a unit of work | Orchestrator |
| `agent_returned` | that subagent returns its condensed result | Orchestrator |
| `dialectic_round` | one generator↔adversary round | the pair |
| `decision` | a notable/ADR-worthy decision | Architect/Implementer |
| `gate` | a human gate reached (e.g. spec-review) | Orchestrator |
| `escalation` | deadlock / risk tie / needs-human | Orchestrator |
| `pr_opened` / `pr_merged` | PR lifecycle | Implementer/Integrator |
| `note` | freeform annotation | any |
| `cycle_completed` | cycle ends (shipped or stopped) | Orchestrator |

**Who emits `agent_dispatched`/`agent_returned`:** Always the Orchestrator —
regardless of whether the subagent is a branded `swarm:*` agent or a general-
purpose Agent-tool subagent. Branded agents may emit their own internal events
(`decision`, `dialectic_round`, `pr_opened`/`pr_merged`, `note`), but the
dispatch/return pair is the Orchestrator's responsibility. A cycle that skips
these events will produce an empty checklist and an unrenderable debrief.

**Pairing:** `agent_dispatched` and `agent_returned` are matched by
`(agent, task|detail)` — keep `--detail`/`--task` identical across the pair so the
checklist closes the item. Record `--tokens` when known (even rough) so cost is
visible.

## The live checklist (the human's window into the run)

The Orchestrator (via the Scribe) keeps a **single GitHub issue comment** current,
refreshed at every boundary:

1. Render: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" checklist --cycle <issue#>`.
2. The output is wrapped in `<!-- swarm:progress cycle=N -->` … `<!-- /swarm:progress -->`
   markers. **Find the existing progress comment and edit it in place** (match the
   marker); create it once at `cycle_started` if absent. One comment, edited —
   never a stream of new comments.

This is the async-durable surface (a new user watching the issue sees live state);
Claude Code is the sync surface where the Orchestrator narrates in parallel.

## Rules

- Append-only: never rewrite past events; correct with a `note`.
- The raw `.swarm/run-log.jsonl` is local machine instrumentation (gitignored).
  The **durable** record is the issue comment + the `debrief` (see the `debrief`
  skill) + ADRs — that is what the Improver and new users read.
