---
name: review-checklist
description: The independent code-review methodology the Reviewer applies to a PR — correctness, tests, risk, reuse, contracts — with a severity+confidence finding schema. Invoked by the Reviewer. Not for general use.
user-invocable: false
---

# review-checklist

Independent verification of a PR against its spec and acceptance criteria. The
reviewer is an adversary on a different model; **agreeableness is failure**, but
so is inventing blockers — score by confidence.

## Checklist

**Correctness**
- Does it satisfy the spec / acceptance criteria, including the edges the issue
  named?
- Failure modes: empty/huge/concurrent/partial-failure inputs; ordering;
  idempotency; rollback.

**Tests**
- Do tests cover the *changed behavior* and its edges (not just the happy path)?
- Would they actually catch a regression? Run them.

**Risk surfaces** (escalate if mishandled)
- `risk:auth` — access control intact, no privilege escalation, sessions sound.
- `risk:money` — units (cents vs dollars), rounding, currency, idempotent charges.
- `risk:data` — migration reversible/backfilled, no data loss, safe ordering.
- `risk:api` — backward-compatible contract, versioning, deprecation path.
- `risk:destructive` — guarded, reversible or gated.

**Reuse & simplicity**
- Is there a smaller/clearer change? Dead code? Duplicated logic? Hidden coupling?

**Hygiene**
- No secrets/keys in the diff; no debug cruft; follows repo conventions.

## Finding schema

Each finding:

```
[blocker|concern|nit] (confidence: high|med|low) <one-line rationale> — path:line
```

- **blocker** — must fix before merge. Don't raise low-confidence blockers.
- **concern** — fix or explicitly accept with reasoning.
- **nit** — optional.

Lead with the single most important finding. Engage the author's rebuttals
rather than re-asserting. Loop to convergence or the lane cap
(Express 1 · Standard 2 · Deep 3); deadlock → escalate with the crux.

## Verdict

`approve` (no open blockers, tests green, risk addressed) · `iterate` · `escalate`.
