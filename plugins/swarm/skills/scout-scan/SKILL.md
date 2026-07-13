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

## Pin hygiene

Whenever a scan touches an existing `adopt`/`adapt` row for any reason (routine
re-pin, a `revisit_if` check, or an unrelated pass over `dependencies.md`),
re-verify the *currently recorded pin* against the dependency's own
primary-source manifest (e.g. its `plugin.json`) — don't just trust the prior
value. A pin can drift from ground truth (transcription slip, a stale secondary
catalog listing) with nothing else to catch it. When the fact needed is an
exact version string, prefer a raw fetch + parse (e.g. `curl` the manifest and
read the field directly) over an LLM-summarized page fetch — a paraphrased
summary is not a reliable source for an exact string and can silently
contradict another summary of the same underlying value.

## Output

The filled scorecard + verdict + proposed `dependencies.md` row, filed as an
`external`-labeled `learning-proposal`. A tripped `revisit_if` → propose
**Retire** (`retire-candidate`).
