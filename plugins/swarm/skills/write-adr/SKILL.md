---
name: write-adr
description: Writes an Architecture Decision Record into docs/decisions/ capturing context, the decision, rejected alternatives, and consequences. Invoked by the Scribe/Architect for lasting decisions. Not for general use.
user-invocable: false
---

# write-adr

Record a lasting decision as an ADR so the *why* survives the agents that made
it. Use for architectural/contract/risk decisions — not every small choice.

## Filename

`docs/decisions/NNNN-short-kebab-title.md` (zero-padded sequential number).

## Template

```markdown
# NNNN. <Title>

- **Status:** proposed | accepted | superseded by NNNN
- **Date:** YYYY-MM-DD
- **Issue/PR:** <links>
- **Deciders:** <agents/humans>

## Context
What forces are at play? Constraints, requirements, risk flags.

## Decision
The choice, stated plainly.

## Rejected alternatives
- <Alternative> — why not (steelman it first, then the deciding tradeoff).

## Consequences
Positive, negative, and follow-ups. New `revisit_if` triggers for the ledger?

## Risk
Which `risk:*` flags applied and how they were mitigated / gated.
```

## Rules

- **Always** fill "Rejected alternatives" — an ADR without them is a changelog.
- Link the originating issue/PR and any spec under `specs/<issue-id>/`.
- Never edit an accepted ADR's decision; supersede it with a new one.
