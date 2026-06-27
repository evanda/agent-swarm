---
name: promote-learning
description: Routes a lesson on two axes — WHERE (shared swarm vs project repo) and LAYER (constitution/skill/CLAUDE.md/learnings) — using portability/stack/class litmus tests. Invoked by the Scribe and Improver. Not for general use.
user-invocable: false
---

# promote-learning

Decide **where** a lesson lives and **at what layer**, before its PR. Both axes
land in the same reviewed queue.

## Axis A — WHERE (shared `swarm` vs a project repo)

Core question: *would this rule be true in a different project of a different
type?* Three litmus tests:

1. **Portability** — want it in a brand-new unrelated project? → **shared**.
2. **Stack** — does it name a framework/file/service/schema/domain term unique to
   this repo? → **project**.
3. **Class** — can you name the general failure *class*? The class rule → shared;
   the instance may leave a local note.

**Split is common:** general principle → shared; local application → project.
*(e.g. "verify external API contracts in tests" → shared; "our webhook sends
cents not dollars" → project.)*

**Defaults:** ambiguous → shared **proposal** (reviewed, downgradable). **Never**
push a stack-specific rule to shared — it pollutes every repo's context.

## Axis B — LAYER

| Nature | Layer |
|---|---|
| non-negotiable | `constitution.md` (shared) / `constitution.delta.md` (project) |
| procedure / methodology | a **skill** |
| convention | `CLAUDE.md` |
| tentative / not yet proven | `learnings.md` |

Lessons **start in `learnings.md`** and harden into a skill or the constitution
only after they **recur**.

## Axis C — POSTURE (for external findings, set by the Scout)

`adopt` / `adapt` / `author` / `retire` — record in `dependencies.md` with a pin
(adopt) or a `revisit_if` trigger (adapt/author).

## Output

A tagged proposal: WHERE · LAYER · (POSTURE) · target file · exact edit · scope
rationale. Filed as a `learning-proposal` issue for the Improver to batch.
