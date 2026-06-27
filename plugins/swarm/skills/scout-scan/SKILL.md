---
name: scout-scan
description: Scorecard methodology for evaluating an external tool/practice/release — Fit, Maturity, Maintenance-delta, Portability, Migration-cost/reversibility, Risk → Adopt/Adapt/Watch/Pass. Invoked by the Scout. Not for general use.
user-invocable: false
---

# scout-scan

Score one external finding and produce a verdict. The default bias is
**conservative** — Watch beats a premature Adopt.

## Scorecard

Rate each dimension (low / med / high) with a one-line justification:

| Dimension | Question |
|---|---|
| **Fit** | Does it match a real need we have (a ledger row, a pain point)? |
| **Maturity** | Production-ready? Releases, adoption, issue hygiene, docs? |
| **Maintenance-delta** | How much of *our* DIY does adopting it let us delete? |
| **Portability / lock-in** | Does it tie us to one stack/vendor/runtime? |
| **Migration cost & reversibility** | Effort to adopt; how easy to back out? |
| **Risk** | New attack surface, instability, license, governance? |

## Verdict

- **Adopt** — high Fit + high Maturity + meaningful Maintenance-delta + acceptable
  lock-in/reversibility. Pin a `ref`/`sha`. Validate with `eval-dependency` first.
- **Adapt** — good Fit but needs a wrapper/extension; record `delta` + `revisit_if`.
- **Watch** — promising but immature, or reversibility/portability unclear. The
  **default**. Add/refresh a `revisit_if` trigger.
- **Pass** — poor Fit or redundant.

## Anti-thrash

- Watch is the default for immature things; require a maturity bar before Adopt/
  Adapt; weight reversibility and portability heavily; never adopt without a
  reviewed PR.

## Output

The filled scorecard + verdict + proposed `dependencies.md` row, filed as an
`external`-labeled `learning-proposal`. A tripped `revisit_if` → propose
**Retire** (`retire-candidate`).
