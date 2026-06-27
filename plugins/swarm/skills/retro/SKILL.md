---
name: retro
description: Structured retrospective on recent swarm work — what went well, what failed, and which lessons to propose. Produces learning-proposal candidates. Invoked by the /swarm:retro command and the Scribe. Not auto-triggered.
user-invocable: false
---

# retro

A structured retrospective on a slice of recent work (an issue, a sprint of
PRs, or a time window). Output is **lesson candidates**, not vibes.

## Inputs

- The run log (`.swarm/run-log.jsonl`), PRs/issues in scope, dialectic outcomes,
  ADRs, and any post-merge defects.

## Prompts

1. **Outcomes** — what shipped, what reverted, what escalated, what's still open?
2. **What worked** — keep-doing patterns (and is the lesson general enough to be
   worth recording?).
3. **What failed** — defects, deadlocks, rubber-stamps, false-blocks, scope
   creep, missed risk. For each, name the **failure class**.
4. **Adversarial health** — were generators and adversaries genuinely on
   different models? Did critiques engage or rubber-stamp?
5. **Cost/effort fit** — was the lane right? Over- or under-powered?

## Output

For each lesson worth keeping, a candidate for `promote-learning`:
- **failure/success class** · **proposed rule** · **layer** (constitution / skill
  / CLAUDE.md / learnings) · **scope** (shared / project) · evidence links.

Hand candidates to the Scribe to file as `learning-proposal` issues. Remember:
lessons **start in `learnings.md`** and harden only after they recur.
