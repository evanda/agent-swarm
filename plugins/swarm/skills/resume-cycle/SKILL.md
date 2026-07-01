---
name: resume-cycle
description: How the Orchestrator recovers an interrupted cycle by rebuilding its own state from the durable record (run-log + issue graph + PRs/worktrees) and continuing from the frontier — re-dispatching only the incomplete stages. Invoked by /swarm:start when a cycle already has prior state. Not for general use.
user-invocable: false
---

# resume-cycle

Recovering a swarm run is **not** a thread resume. The Orchestrator is the main
session instance; subagents are cattle. When a run is interrupted — session lost,
machine crashed, Esc pressed mid-flight — you do not reattach to a conversation.
You **reconstruct the Orchestrator from state that lives in Git** (principle 6)
and continue the cycle from where the durable record says it stopped.

Resuming one subagent (e.g. `SendMessage` to a live Implementer) only recovers
that one leg. The pipeline it sits in — Reviewer (different model), Integrator
merge, Scribe debrief — is driven by *you*, the Orchestrator, and only a rebuilt
Orchestrator can drive it. This skill is that rebuild.

## Step 1 — Rehydrate from the record

Read the cycle's prior state. Source of truth, richest first:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" status   --cycle <issue#>
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" checklist --cycle <issue#>
```

This replays `.swarm/run-log.jsonl` → lane, every `agent_dispatched`/`returned`,
dialectic rounds, gates, escalations, PRs. **If the log is absent** (you're on a
different machine — it's gitignored/local), rebuild the same picture from the
durable surfaces instead: the `<!-- swarm:progress cycle=N -->` checklist comment
on the issue, plus the issue graph below.

## Step 2 — Reconcile against ground truth (reality wins)

The log records what was *intended and reported*; it can lag what actually
happened. Check the live world and **trust it over the log** on conflict:

- **Locks / claims** — list the cycle's sub-issues with their `in-progress`
  label and assignee. An assigned + `in-progress` sub-issue is claimed work.
- **PRs** — open/draft PRs per sub-issue: which implementation legs produced
  output, and whether any already merged.
- **Worktrees** — `git worktree list` for `agent-*` trees holding in-progress
  changes on disk.

Where reality and the log disagree (log says dispatched, no PR exists; log silent
but a PR is open; a PR merged that the log never recorded), **append a `note`**
recording the correction. Never rewrite past events — the log is append-only.

**Never trust an interrupted or crashed agent's artifacts at face value.** A
worktree left by a dead background agent (API drop, process restart) can look
complete — fresh mtimes, a plausible diff — while being partial or internally
inconsistent. Before treating that work as done or advancing *any* gate on top
of it, diff the worktree against the spec/critique it was answering and confirm
every item actually landed. Log a `note` naming the crash and the worktree path
so the checklist shows the recovery boundary, not a silent gap.

## Step 3 — Compute the frontier

For each sub-issue, determine the next incomplete stage, using the **already-
stamped lane** (do not re-route) and its caps:

| Lane | review rounds | design dialectic | merge |
|---|---|---|---|
| express | 1 | none | queue |
| standard | cap 2 | none | queue |
| deep | cap 3 / PR | Architect↔Challenger cap 2 (before fan-out) | Integrator |

Stage order per unit: implement → review (round *n* of cap) → merge. Cycle-level:
after all units merge → Scribe debrief → `cycle_completed`. The frontier is the
first stage in each chain that is not yet `done`.

## Step 4 — Re-dispatch only the incomplete stages

Drive the lane forward from the frontier, **skipping anything already done**:

- **Honor unmet gates first.** A logged `gate` (e.g. `spec-review`) or open
  `escalation` with no resolution **stops the resume** — surface it to the human;
  do not fan out past a gate.
- **Implementer.** If a sub-issue's implementation isn't `done`: re-dispatch a
  fresh Implementer against the same sub-issue and worktree (cattle — a new
  instance picks up the claim and the on-disk work). Only `SendMessage`-resume a
  prior Implementer if that task is genuinely still alive and cheaper to continue.
  If the prior instance died mid-task, the fresh Implementer's first job is to
  verify the inherited worktree against the spec/critique (Step 2) before
  continuing or redoing it — never assume a crashed instance's partial work is
  either complete or safely discardable.
- **Reviewer.** A returned Implementer whose Reviewer never ran needs a **fresh
  Reviewer on a different model** — the pairing and different-model rules hold on
  resume exactly as on a first pass. An agent never reviews its own PR.
- **Integrator / Scribe.** These are *your* legs — they were always separate
  dispatches, never something the Implementer did. Drive them once the units are
  green: Integrator for the merge queue, then Scribe for decisions + debrief.

## Step 5 — Re-instrument and converge

Keep the run legible across the seam (the `run-log` skill is the contract):

1. Append a marker so the timeline shows the recovery:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" log --cycle <issue#> \
       --event note --detail "cycle resumed from frontier: <one-line state>"
   ```
2. Refresh the live checklist comment (`swarm_log.py checklist`) so the human sees
   accurate state immediately.
3. Proceed through the normal lane flow to `cycle_completed` + debrief.

## Rules

- **Don't re-route.** The lane is already stamped; resume continues it. Re-route
  only if the human explicitly asks (scope changed).
- **Don't redo done work.** Never re-open or duplicate a merged PR; never re-run a
  completed review that converged.
- **Append-only.** Correct the record with `note`s; never edit past events.
- **Gates still bind.** A resume cannot walk past a human gate or open escalation.
