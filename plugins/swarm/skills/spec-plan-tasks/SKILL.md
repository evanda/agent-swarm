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
3. **plan** → write `specs/<issue-id>/plan.md`:
   - Approach; **key decisions with rejected alternatives + why**; affected
     components; data/contract impact; **test strategy**; rollout/rollback.
4. **tasks** → write `specs/<issue-id>/tasks.md`:
   - One delegatable task per future Implementer. Each: independently testable,
     clear file/scope boundary so parallel tasks don't collide, explicit
     acceptance check. These become sub-issues.
5. **clarify** — list open questions that block fan-out. Resolve with the
   Orchestrator/human before proceeding.

## Gates

- Run the **Architect↔Challenger `dialectic`** (cap 2) on spec+plan **before**
  emitting final tasks.
- Deep-lane specs require the **human gate** (`spec-review` label) before fan-out.

## Output

Paths to spec.md / plan.md / tasks.md, the proposed sub-issue list, and the list
of decisions worth an ADR (hand to `write-adr`).
