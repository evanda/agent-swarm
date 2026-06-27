# 0002. Observability: live progress + comprehensive debriefs

- **Status:** accepted
- **Date:** 2026-06-27
- **Issue/PR:** observability work on `claude/swarm-master-build-infra-2gt06c`
- **Deciders:** Evanda (human), build agent

## Context

A swarm cycle burns many tokens and runs work across ephemeral subagents whose
context is, by design, isolated from the main thread. That isolation is the
efficiency mechanism, but it makes a run **opaque**: a user (especially a new one)
can't tell what's happening, what it cost, or what went into a decision. The spec
asserts principle #7 ("every run is instrumented") and lists `.swarm/run-log.jsonl`
in the paper trail, but provided no human-facing view or after-action report.

## Decision

Instrument every boundary as structured events in `.swarm/run-log.jsonl`, and
**render** two human views from those same events (so they can't drift):

1. **Live checklist** — a single GitHub issue comment, edited in place between
   `<!-- swarm:progress -->` markers, refreshed by the Scribe at each boundary.
   `/swarm:status` renders it on demand.
2. **Debrief** — a comprehensive end-of-cycle report posted to the issue and
   optionally committed to `docs/debriefs/<issue#>.md`, configurable via
   `.swarm/config.json` `debrief` (`issue` | `commit` | `both`; default `issue`).

Mechanism: `scripts/swarm_log.py` (log / checklist / debrief / cycles) is the one
deterministic renderer; the `run-log` and `debrief` skills define the contract;
the Scribe owns emission and publishing; the Orchestrator drives the boundaries.

## Rejected alternatives

- **A third human surface (pastebin / external dashboard).** Rejected: violates
  the "two human surfaces only" principle (GitHub Issues + Claude Code). GitHub
  Issues already is the async-durable surface; reuse it.
- **Commit `run-log.jsonl` as the durable record.** Rejected: a per-run,
  append-only JSONL committed from parallel worktrees invites merge conflicts and
  repo noise. Keep it local/gitignored as the *machine* layer; the durable record
  is the issue comment + the (optionally committed) debrief + ADRs.
- **Free-form markdown written by hand per run.** Rejected: drifts from reality
  and isn't machine-parseable for the Improver. Render from the event log instead.
- **Always commit debriefs.** Rejected as a forced default (repo noise for teams
  that don't want it); made configurable, defaulting to issue-only.

## Consequences

- New users get a live window and a readable after-action report; the Improver
  gets a clean, structured input (the log) plus a human synthesis (the debrief).
- Adds one closed event vocabulary that all agents must use — kept in lockstep
  between `scripts/swarm_log.py` and the `run-log` skill.
- `revisit_if`: if a first-class progress/telemetry primitive appears in Claude
  Code or the GitHub tooling, reconsider the hand-rolled renderer (ledger).
