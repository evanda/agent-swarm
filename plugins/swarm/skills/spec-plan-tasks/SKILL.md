---
name: spec-plan-tasks
description: Turns an ambiguous Deep-lane issue into spec → plan → tasks artifacts under specs/<issue-id>/, wrapping Spec Kit (constitution → specify → plan → tasks → clarify). Invoked by the Architect. Not for general use.
user-invocable: false
---

# spec-plan-tasks

Produce fan-out-ready artifacts for a Deep-lane issue. This wraps **Spec Kit**
(`github/spec-kit`, pinned in `dependencies.md`); use its commands where present,
otherwise produce the same artifacts by hand. The wrapper adds our lane gates and
decision-recording requirement.

## Stages

1. **constitution** — load the shared `constitution.md` + the repo's
   `constitution.delta.md`. These are binding inputs.
2. **specify** → write `specs/<issue-id>/spec.md`:
   - Problem, goals, **non-goals**, acceptance criteria, risks, affected users.
   - For user-facing tasks: add **usability acceptance criteria** alongside the
     functional ones — what the user must perceive/experience: visible state
     change, viewport follows the update, tap targets ≥ 44 pt/dp, feedback on
     action, empty/error states handled. Functional-only criteria are incomplete
     for UI work.
   - **Split compound ACs.** An acceptance criterion joining two independently-
     buildable behaviors with "AND" (e.g. "a pre-check gate AND a post-rejection
     signal"; "input is validated AND the error is displayed") must be written —
     and later verified — as **two separate criteria**, each with its own check.
     A single combined check can pass via either half alone doing the work,
     letting the other ship unbuilt. Ask: does the test path for this AC exercise
     *both* halves, or could either one alone make it pass?
3. **plan** → write `specs/<issue-id>/plan.md`:
   - Approach; **key decisions with rejected alternatives + why**; affected
     components; data/contract impact; **test strategy**; rollout/rollback.
   - **Split-authority design-smell check**: if a value is *produced* by one side
     of a trust/authority boundary (e.g. client-predicted) and *consumed* or also
     *mutated* by the other (e.g. server-adjudicated), don't model it as owned by
     one side only — pin the explicit **reconciliation model** (server-absolute,
     or client-owned with server-applied deltas/ledger) before fan-out. A field
     both sides mutate is a flag to resolve at design time, not defer to review.
4. **tasks** → write `specs/<issue-id>/tasks.md`:
   - One delegatable task per future Implementer. Each: independently testable,
     clear file/scope boundary so parallel tasks don't collide, explicit
     acceptance check. These become sub-issues.
   - **Batch micro-tasks**: if two or more tasks are trivially small (≤ ~50 lines,
     same component, no independent design risk), combine them into one task. The
     Implementer lifecycle overhead (claim → worktree → implement → review → merge)
     is substantial — one task per *unit of review*, not per line changed.
   - **Minimize the serial spine**: explicitly identify which tasks are independent
     (fan-out safe). State the critical-path length in tasks.md as a planning
     metric; if it exceeds 3 sequential hops, challenge the decomposition.
   - **Pin shared contracts**: when tasks fan out in parallel across a shared
     interface (a data shape, event payload, field name produced by one task and
     consumed by another), pin the exact shape as a named contract in tasks.md
     that every side codes against — don't leave each task to infer it and
     reconcile the mismatch at integration.
   - **Cross-component integration smoke**: when the milestone spans a
     client↔server or other multi-component boundary, add an early **integration
     smoke task** (two real endpoints actually exchanging state) as its own task,
     placed *before* the big fan-out — a cheap headless probe is enough. The
     acceptance criteria must include this real end-to-end check, not only
     per-package unit suites; components can each pass in isolation while the
     integration between them is broken. If the milestone adds a **CLIENT-
     consumed server callback or synced field**, the probe must drive the real
     client's actual bootstrap/wiring path (not just the SDK/client object in
     isolation) — a wiring shim between the SDK and the app can silently drop
     fields that a direct-SDK test never exercises (see `review-checklist`).
5. **clarify** — list open questions that block fan-out. Resolve with the
   Orchestrator/human before proceeding.

## Gates

- Run the **Architect↔Challenger `dialectic`** (cap 2) on spec+plan **before**
  emitting final tasks.
- Deep-lane specs require the **human gate** (`spec-review` label) before fan-out.

## Output

Paths to spec.md / plan.md / tasks.md, the proposed sub-issue list, and the list
of decisions worth an ADR (hand to `write-adr`).
