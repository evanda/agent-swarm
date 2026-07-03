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
- Would they actually catch a regression? Run the repo's **full configured
  verification set** — typecheck **and** test **and** lint/format (whatever
  `package.json`/CI defines) — not just typecheck+test. A lint/format failure is
  at least a nit; treat it as blocking if it's already on `main`.
- **Run economically.** To confirm a specific block/test actually executed
  (e.g. the "named `[SEC]` block ran" check below), run *that block only*,
  targeted + verbose, plus its mutation check — not the whole suite verbose. One
  final full-suite run with the dot/default reporter is sufficient to confirm
  overall green; don't re-run the full verbose suite repeatedly.
- For any test asserting a *specific mechanism* prevents a failure (mandatory for
  `[SEC]`/`risk:security`): verify it's **non-vacuous** — disable or mutate the
  mechanism and confirm the test fails. A test that passes whether or not the
  mechanism runs is a false guard. Corollary: a design blocker resting on assumed
  framework behavior must be source- or spike-verified, not taken from docs alone.
- If the PR changes a **client-server wire boundary** (SDK version bump, message/
  event schema, new client library integration): does a **real-client smoke
  test** exercise the actual SDK/client against a real (not faked/stubbed) server
  instance — not just tests that mock the transport layer? Verify it's
  mutation-tested (temporarily reintroduce the bug; confirm only that test
  fails). Unit tests that fake the transport can't catch a transport-layer/SDK-
  version mismatch, however green the suite is. For a milestone that adds a
  CLIENT-consumed server callback/synced field, the real-client probe must drive
  the actual bootstrap/wiring path the production client uses (not just the SDK
  client object directly) — a wiring shim between the SDK and the app can drop
  fields that direct-SDK tests never see.

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

**UX & usability** (user-facing tasks only)
- Visibility of state: does the user see what changed? Does the viewport follow
  the updated element (enabling content ≠ content appearing off-screen)?
- Affordance & discoverability: are interactive elements visibly actionable?
- Tap/click targets: ≥ 44 pt/dp (mobile HIG); targets must not overlap each other.
- Feedback on action: every user action produces a visible response before the
  next interaction is available.
- Empty / loading / error states: handled and communicated, not silently blank.
- Accessibility: semantic markup / ARIA where applicable; colour contrast sufficient.

Missing UX acceptance criteria in the spec is itself a **concern** — flag it.

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
