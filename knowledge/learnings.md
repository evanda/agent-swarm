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
- **Status:** recurring (confirmed 2026-06-30 scout cycle: re-pinned spec-kit @v0.11.9 → @v0.12.1 after verifying revisit_if not tripped; confirmed again 2026-07-01: re-pinned @v0.12.1 → @v0.12.2, a bug-fix/integration-hygiene patch, revisit_if still not tripped).

## 2026-06-29 — Track a native substrate before adapting the core onto it
- **Context:** Scout finding #12 — Claude Code shipped native **Dynamic Workflows** (research preview, 2026-05-28; v2.1.154+): Claude writes a JS orchestration script running ≤16 concurrent / 1000 total subagents, with same-session resume and a built-in adversarial cross-check pattern. This is the native substrate for the fan-out + durable-state + cross-check mechanics our Orchestrator hand-rolls — yet `agent-orchestration` had **no ledger row**.
- **Failure class:** A core capability the swarm *authors* can have a native equivalent appear upstream while remaining untracked, so no `revisit_if` ever fires — the divergence ledger silently misses our biggest DIY surface.
- **Lesson:** When a native substrate appears for something we author, **add the ledger row first** (posture `author` + a `revisit_if`) and keep authoring; do **not** refactor the core onto a research-preview API. Adapt only once it exits preview with a stable API *and* cross-session-durable resume (workflow resume is same-session only, so it cannot yet replace `swarm_log.py`'s cross-session run-log). Our durable value-add (roles × risk lanes × independent-reviewer gates × run-log) is complementary to the substrate, not replaced by it.
- **Scope:** shared.
- **Status:** recurring (confirmed 2026-07-01 scout cycle: Scout finding #23 found Dynamic Workflows' research-preview label dropped from docs — Condition 1 of the `revisit_if` met — but Condition 2, cross-session-durable resume, explicitly not met; ledger `delta` updated to record partial-trigger status, posture kept `author`, no adapt spike started).

## 2026-06-27 — Adopt complementary tools as a floor, not a replacement
- **Context:** Scout finding #5 — Anthropic's official `security-guidance` pre-tool hook (~25 dangerous-write patterns) overlaps our DIY `guard.py` + `red-team`.
- **Failure class:** "delete our DIY" can over-correct — replacing a swarm-specific guard with a generic tool would drop our own invariants.
- **Lesson:** Treat a maintained generic tool as a **safety floor beneath** our bespoke layer, not a swap: keep `guard.py` for swarm invariants and let the external plugin cover the generic SAST surface we choose not to hand-roll. The ledger `adopt` row waited for a concrete release pin (ledger rule: every `adopt` row MUST carry a pin); now pinned at `security-guidance@2.0.6` (requires Claude Code ≥ v2.1.144) and shipped as the `write-time-security-guard` row — resolving #5.
- **Scope:** shared.
- **Status:** tentative.

## 2026-06-30 — Never trust an interrupted agent's artifacts before a gate
- **Context:** Issue #28, retro from evanda/bub#187 — the same root cause (a
  multi-file edit left silently partial, but looking complete) recurred via two
  different triggers: a mid-response API drop, then a background agent dying on
  a process restart. Both times the only thing that caught it was the
  Orchestrator manually grepping the worktree.
- **Failure class:** interrupted work in a worktree can look done (fresh mtimes,
  a plausible diff) while being partial or internally inconsistent; treating its
  presence as its completeness lets broken state pass a gate silently.
- **Lesson:** hardened into a standing step — `resume-cycle` now requires
  diffing an inherited/crashed agent's worktree against the spec/critique before
  trusting it or advancing any gate, and `run-log` documents closing a dead
  dispatch with `agent_returned --status blocked` + a `note` so the crash is a
  visible checklist marker instead of a silent gap. The broader engineering asks
  from #28/#29 (auto-checkpoint of WIP, resume-from-journal reattach, a live
  swimlane UI) remain open — this promotion covers the process rule only.
- **Scope:** shared.
- **Status:** promoted-to(resume-cycle skill, run-log skill).
