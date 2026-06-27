---
name: eval-dependency
description: Validates a candidate external dependency against the golden evals before recommending Adopt — confirms it meets fit and causes no regression. Invoked by the Scout. Not for general use.
user-invocable: false
---

# eval-dependency

Before the Scout recommends **Adopt/Adapt**, validate the candidate against the
golden evals so the recommendation is evidence-backed, not vibes.

## Process

1. **Define the swap.** What capability would the candidate replace or augment?
   Find its row in `dependencies.md` (or note that it would add one).
2. **Pin it.** Reference a specific `ref`/`sha`/tag — never "latest".
3. **Run the evals against the candidate's behavior:**
   `python3 knowledge/evals/run.py --llm` with the candidate wired in (or a
   focused subset that exercises the affected capability).
4. **Compare** to the current baseline: regressions, parity, improvements.
5. **Reversibility check** — confirm you can back the change out cleanly.

## Output

An evidence packet for the proposal:
- eval results (candidate vs baseline; any regressions are disqualifying for
  Adopt),
- pinned reference,
- migration & rollback notes,
- recommended posture (`adopt` / `adapt` / `watch`) with the `revisit_if`/pin.

If the candidate regresses any eval, it cannot be **Adopt** — downgrade to
**Watch** with the failing case recorded.
