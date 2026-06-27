# Learnings

Accumulated lessons from the inward loop (retros, interrogations, traces).
Lessons **start here** as tentative notes and harden into a skill or the
constitution only after they recur. Each entry is appended by the Scribe or the
Improver via a reviewed PR — never edited silently.

Format per entry:

```
## YYYY-MM-DD — <short title>
- **Context:** what was happening (issue/PR link).
- **Failure class:** the general class, not just the instance.
- **Lesson:** the rule to apply next time.
- **Scope:** shared | project (see promote-learning litmus tests).
- **Status:** tentative | recurring | promoted-to(<target>).
```

---

<!-- New learnings are appended below this line. -->

## 2026-06-27 — Pin upstream by release, never `@latest`
- **Context:** Scout finding #4 — `spec-plan-tasks` ledger row pinned `github/spec-kit@latest`. Spec Kit shipped 55+ releases and reached v0.11.9, tripping the `revisit_if` for native gates.
- **Failure class:** `adopt`/`adapt` rows pinned to a moving ref drift silently — behavior changes before it is vetted, defeating the divergence ledger.
- **Lesson:** Every `adopt`/`adapt` row carries a concrete `ref`/`sha`/tag (here: `@v0.11.9`); the Scout re-pins on each scan rather than relying on `@latest`. When a `revisit_if` trips, prefer **narrow the wrapper to our genuine value-add** (risk-aware lane mapping) over wholesale retire.
- **Scope:** shared.
- **Status:** tentative.

## 2026-06-27 — Adopt complementary tools as a floor, not a replacement
- **Context:** Scout finding #5 — Anthropic's official `security-guidance` pre-tool hook (~25 dangerous-write patterns) overlaps our DIY `guard.py` + `red-team`.
- **Failure class:** "delete our DIY" can over-correct — replacing a swarm-specific guard with a generic tool would drop our own invariants.
- **Lesson:** Treat a maintained generic tool as a **safety floor beneath** our bespoke layer, not a swap: keep `guard.py` for swarm invariants and let the external plugin cover the generic SAST surface we choose not to hand-roll. Defer the ledger `adopt` row until a concrete release pin is chosen (ledger rule: every `adopt` row MUST carry a pin) — tracked by #5; no unpinned row shipped.
- **Scope:** shared.
- **Status:** tentative.
