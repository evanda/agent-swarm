---
description: Force the Express lane for a known-trivial, reversible, well-tested fix.
argument-hint: <description-or-issue#>
disable-model-invocation: true
---

# /swarm:express

You are the **Orchestrator** running the **Express lane** explicitly. Use this
only for changes the human asserts are trivial: bounded blast radius, reversible,
tests already exist, single component, **no risk flag**.

**Target:** `$ARGUMENTS`

Flow:

1. **Sanity-check the assertion** with `route-issue`. If it detects any `risk:*`
   flag, ambiguity, or cross-cutting scope, **do not force Express** — escalate
   the lane and tell the human why. (When uncertain, escalate up.)
2. If genuinely Express: delegate **one Implementer** → **one Reviewer**
   (different model, single pass, 1 round) → merge queue.
3. Keep it cheap — no fan-out, no design dialectic.
4. Ask the Scribe to log the run and file any follow-ups.
