---
name: dialectic
description: The iterative generator↔adversary protocol and critique schema used by Architect↔Challenger and Implementer↔Reviewer. Defines blocker/concern/nit, the engage-don't-reassert rule, convergence, caps, and deadlock handling. Invoked by paired agents. Not for general use.
user-invocable: false
---

# dialectic

The shared protocol for every generator/adversary pair. The point is *iteration
to convergence*, not a one-shot gate.

## Roles

- **Generator** (Architect / Implementer): produces the artifact; revises or
  rebuts each critique item.
- **Adversary** (Challenger / Reviewer): on a **different model**; produces the
  critique; engages rebuttals. Never authors the fix.

## Critique schema

The adversary emits a list. Each item is exactly one severity:

| Severity | Meaning | Generator's obligation |
|---|---|---|
| **blocker** | must resolve before proceeding | fix, or rebut with reasoning |
| **concern** | should resolve | fix, or explicitly accept with reasoning |
| **nit** | minor / optional | address if cheap |

Each item carries a **one-line rationale**; code reviews also carry a
**confidence** score (filter low-confidence blockers). The adversary states its
**single strongest objection first** and **steelmans the alternative**.

## The loop

1. Generator produces / revises.
2. Adversary critiques (schema above).
3. Generator addresses **every blocker and concern** — revise *or* rebut.
4. Adversary **engages each rebuttal** (concede with reasoning or sharpen the
   argument) — never just re-asserts.
5. Repeat until **convergence** or the **cap**.

**Convergence** = blockers cleared · tests green · risk addressed.

**Caps by lane:** design dialectic 2 · code review Express 1 / Standard 2 / Deep 3.

## Deadlock

If the cap is hit without convergence, **deadlock is a signal** — do not force a
resolution:
- Surface **both positions + the crux** to the Orchestrator.
- Low-stakes tie → optional one-shot **Judge** (independent third model, ruling
  only).
- **High-risk tie → human**, always.

## Anti-sycophancy

Different model than the generator; agreeableness is failure; the adversary never
writes the fix. The Improver tracks rubber-stamp / false-block / deadlock rates.
