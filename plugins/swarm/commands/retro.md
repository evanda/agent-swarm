---
description: Run a retrospective on recent swarm work and produce learning-proposals.
argument-hint: [issue# | PR# | time-window]
disable-model-invocation: true
---

# /swarm:retro

Run a structured retrospective via the **`retro`** skill over the scope in
`$ARGUMENTS` (an issue, a set of PRs, or a time window; default: recent work).

1. Gather the run log, PRs/issues, dialectic outcomes, ADRs, and any post-merge
   defects in scope.
2. Work through the `retro` prompts — outcomes, what worked, what failed (name the
   failure class), adversarial health, cost/effort fit.
3. For each keeper lesson, route it with **`promote-learning`** (WHERE: shared vs
   project; LAYER: constitution/skill/CLAUDE.md/learnings).
4. Have the **Scribe** file the results as `learning-proposal` issues so the
   Improver can batch them into a reviewed PR. Remember: lessons start in
   `learnings.md` and harden only on recurrence.
