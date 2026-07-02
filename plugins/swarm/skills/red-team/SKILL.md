---
name: red-team
description: Risk-mode adversarial checklist applied when a risk flag is present (auth/money/data/api/destructive). Hunts for abuse, failure, and irreversibility before merge. Invoked by the Challenger/Reviewer on risk-flagged Deep work. Not for general use.
user-invocable: false
---

# red-team

A focused, risk-mode pass layered on top of the normal dialectic when any
`risk:*` flag is present. Think like an attacker and like Murphy.

## By risk flag

**`risk:auth`**
- Privilege escalation, IDOR, missing authz checks, token/session fixation,
  replay, expiry, logout/invalidation, multi-tenant isolation.

**`risk:money`**
- Units (cents vs dollars), rounding/truncation, currency, double-charge,
  idempotency keys, refunds, race on balance, negative/overflow amounts.

**`risk:data`**
- Migration reversibility, backfill correctness, data loss on failure, lock/
  downtime, ordering, partial migration, PII handling.

**`risk:api`**
- Backward compatibility, contract drift, versioning, error-shape changes,
  pagination/limits, deprecation path, consumer breakage.

**`risk:destructive`**
- Reversibility, blast radius, confirmation/gating, dry-run, idempotency, audit
  trail, scope-limiting.

## Non-vacuous mechanism check

A `[SEC]` test that *names* a mechanism as the thing preventing a failure must be
proven to actually depend on it: disable or mutate the mechanism and confirm the
test then fails. A test that passes either way is a vacuous guard — false
confidence on exactly the work where a miss is a cheat hole. If a design
decision or dialectic blocker rests on an assumed framework/library behavior,
verify it against source or a spike before relying on it.

## Cross-cutting probes

- What's the worst input? The worst timing (concurrency, retries, partial
  failure)? The worst actor?
- What state can't be undone? Is there a checkpoint/human gate before it?
- Are secrets/credentials touched? (→ hard guard.)

## Output

Findings in the `dialectic` schema (blocker/concern/nit + rationale +
confidence). Any unmitigated `risk:*` blocker → **human gate** before merge.
High-risk ties never resolve by Judge — escalate to a human.
