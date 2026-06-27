---
name: route-issue
description: Conservative risk/ambiguity rubric that classifies a GitHub issue into a lane (express/standard/deep) and stamps risk flags. Invoked by the Orchestrator at intake. Not for general use.
user-invocable: false
---

# route-issue

Classify an issue into exactly one **lane** and stamp any **risk flags**. The
rubric is deliberately conservative: **when uncertain, escalate a lane up.**

## Step 1 — detect risk flags (these dominate)

Scan the issue for these. **Any one forces the Deep lane** (and, combined with
high stakes, a human gate) regardless of how small the change looks:

| Flag | Trigger |
|---|---|
| `risk:auth` | authentication, authorization, sessions, access control, tokens |
| `risk:money` | payments, billing, pricing, currency, financial calculation |
| `risk:data` | schema change, migration, data deletion/backfill |
| `risk:api` | public/external contract (REST/GraphQL/SDK/webhook shape) |
| `risk:destructive` | irreversible ops, bulk mutation, production state |

Secrets/credentials in scope → escalate even without a label.

## Step 2 — pick the lane

Choose the **cheapest lane that is safe**:

| Lane | All of these must hold |
|---|---|
| **`lane:express`** | bounded blast radius · reversible · tests already exist · single component · **no risk flag** |
| **`lane:standard`** | clear intent · small design · localized · no risk flag |
| **`lane:deep`** | ambiguous **or** cross-cutting **or** any risk flag |

Decision order:
1. Any risk flag or secret? → **Deep** (stop).
2. Ambiguous intent or cross-cutting / multi-component? → **Deep**.
3. Clear intent but needs a little design / more than one file of thought? → **Standard**.
4. Trivial, reversible, tested, single component? → **Express**.
5. Genuinely unsure between two lanes? → pick the **higher** one.

## Step 3 — emit

Return and stamp on the issue:

- `lane:<express|standard|deep>`
- zero or more `risk:*` labels
- a one-paragraph **rationale** naming the deciding factors (e.g. "reversible,
  bounded, tests exist → express" or "touches session signing → risk:auth → deep")
- whether a **human gate** is required (Deep spec gate, or any high-stakes risk tie)

## Adversarial depth (wire this through)

Lane sets the dialectic depth automatically:

| Lane | Code review rounds | Design dialectic | Red-team |
|---|---|---|---|
| Express | 1 | none | no |
| Standard | cap 2 | none (unless risk flag) | no |
| Deep | cap 3 per PR | Architect↔Challenger cap 2, before fan-out | if any risk flag |
