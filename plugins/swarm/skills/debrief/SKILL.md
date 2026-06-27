---
name: debrief
description: Produces the comprehensive end-of-cycle report from the run log — what every agent did, dialectic outcomes, decisions, gates, PRs, token cost, and candidate learnings. Invoked by the Scribe at cycle end. Not for general use.
user-invocable: false
---

# debrief

The comprehensive after-action report for a swarm cycle. A new user reads it to
understand *what the swarm actually did and what it cost*; the Improver reads it
to mine lessons. Rendered from the run log so it reflects reality, then enriched
by the Scribe.

## Generate

```
python3 scripts/swarm_log.py debrief --cycle <issue#>
```

This produces a markdown report with: header (lane, risk, timing, subagent count,
dialectic rounds, **estimated tokens**), what each agent did, decisions & rejected
alternatives, human gates/escalations, PRs, adversarial-health summary, a
**For the Improver** section, and a full timeline.

## Enrich (Scribe judgment — fill the placeholders)

The renderer leaves marked gaps the Scribe completes:
- **Decisions** — link the actual ADRs in `docs/decisions/`.
- **Adversarial health** — note any rubber-stamp / false-block observed, and
  whether each pair genuinely ran on different models.
- **For the Improver** — distill candidate learnings (failure classes, routing
  misses, cost surprises) and file the keepers as `learning-proposal` issues via
  `promote-learning`.

## Publish (where it lives)

Read `.swarm/config.json` → `debrief` (`issue` | `commit` | `both`; default
`issue`):
- **issue** — post the report as a comment on the cycle's issue (durable, async
  surface; no repo noise).
- **commit** — write `docs/debriefs/<issue#>.md` and commit it (in-repo reference,
  handy for browsing history and for the Scout/Improver).
- **both** — do both.

Always link the debrief from the issue so it is one click from the work.

## Why this matters

It turns an opaque, expensive multi-agent run into an inspectable record — the
single best artifact for onboarding a skeptical new user *and* for feeding the
self-improvement loop. Keep it honest: if a lane was over-powered or tokens
overran, say so — that is exactly the signal the Improver needs.
