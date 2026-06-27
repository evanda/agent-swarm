---
name: interrogate
description: Cross-examination of a past run's decision records to surface root causes and reusable lessons. Sampled by the Improver, weighted toward bad outcomes, low-confidence findings, and risk work. Invoked by the Improver. Not for general use.
user-invocable: false
---

# interrogate

Cross-examine a completed run using its **decision records** (Architect/
Implementer logs, the run log, PR/review history). The goal is the *failure
class* and a reusable lesson — not blame.

## Sampling (the Improver chooses what to interrogate)

Weight toward:
- bad outcomes (reverts, escalations, missed bugs, post-merge defects),
- low-confidence findings that turned out to matter (or didn't),
- risk-flagged work,
- deadlocks and rubber-stamps.

## The cross-examination

For the sampled run, ask:
1. **What was decided, and why?** Pull the recorded rationale and rejected
   alternatives.
2. **What did the adversary catch / miss?** Was a real issue waved through
   (rubber-stamp) or a non-issue blocked (false-block)?
3. **Where did the rationale not survive contact?** Which assumption broke?
4. **Is this an instance of a nameable class?** (e.g. "verified the happy path
   only", "trusted an external contract without a test".)
5. **Smallest change that prevents the class next time?** Which layer
   (constitution / skill / CLAUDE.md / learnings) and WHERE (shared/project)?

## Output

A candidate lesson, ready for `promote-learning`:
- failure class · evidence (links) · proposed rule · layer · scope ·
  confidence that it recurs.

Feeds the Improver's metrics (rubber-stamp / false-block / deadlock rates).
