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

## 2026-07-02 — A routing label must never double as an unattended-work trigger
- **Context:** Issue #9 (downstream repo) — an interactive `/swarm:start` run stamped `lane:standard` on an issue as part of routing; an async scheduled job watching for `lane:*` picked up the same label as its trigger and independently implemented the issue, committing straight to the shared `claude-async` branch with no PR and no review. Two divergent implementations collided; recovery required a manual `git revert`.
- **Failure class:** A label meant for one purpose (routing/telemetry, applied mid-run) was overloaded as a second purpose (async trigger), so an unrelated action (stamping the routing label) silently launched a second, unattended, unreviewed build of the same issue. Compounded by the async path skipping the review gate every other swarm path enforces.
- **Lesson:** Decouple trigger from routing label — `lane:*`/`triage` never themselves launch a run; introduce an explicit opt-in `swarm:async` label as the only async trigger. Any async job-picker must claim-before-work (check for a live claim, skip if present, post its own claim comment) symmetrically with interactive runs, and must land its result through the identical Implementer→Reviewer→merge-queue path — never a direct commit to a shared/integration branch. Hardened into `constitution.md` (new principle 10 + label taxonomy), `orchestrator.md`, `start.md`, `help.md`, and a documented async job-picker contract + routine prompt in the README.
- **Scope:** shared.
- **Status:** promoted-to(constitution.md, orchestrator.md, start.md, help.md, README.md).

## 2026-07-02 — Model choice should route by task class, not stay flat per role
- **Context:** Issue #47 (spacewars M2/M3) — a flat Opus-implement/Sonnet-review policy ran verbatim relocations and doc/lint fixes at the same tier as `risk:security` pickup-adjudication work, while the adversarial passes that caught the real bugs got no upgrade.
- **Failure class:** Model tier left implicit rather than routed means cheap mechanical work overpays (slow + costly) and the hardest adversarial/design work is under-resourced.
- **Lesson:** Extend `route-issue` to stamp a model tier (`fast`/`standard`/`deep`/`adversarial`) per task/role from a matrix in `.swarm/config.json`, on top of the existing lane. The cross-model-review invariant (reviewer ≠ implementer model) still applies as a constraint over tier selection.
- **Scope:** shared.
- **Status:** promoted-to(route-issue skill, .swarm/config.json `model_tiers`).

## 2026-07-02 — Pin shared cross-task interfaces before fan-out
- **Context:** Issue #46 (spacewars M3/M4, recurring across two milestones) — a producer task emitted one event shape while the consumer task expected another; each side inferred independently and integration had to bridge the mismatch.
- **Failure class:** Parallel tasks that share an interface (data shape, event payload, field name) but aren't given a pinned contract will diverge — neither task is individually wrong, the gap is a missing shared spec.
- **Lesson:** `spec-plan-tasks` tasks.md must pin exact shared data shapes/event payloads/field names as a named contract every side codes against, whenever tasks fan out in parallel across a shared boundary.
- **Scope:** shared.
- **Status:** promoted-to(spec-plan-tasks skill).

## 2026-07-02 — Split read/write authority across a trust boundary needs a pinned reconciliation model
- **Context:** Issue #45 (spacewars M3, decision D7a) — a value drained client-side and credited server-side was modeled as server-owned only; the server value never drained and clamped credits no-opped, silently breaking ~50% of pickups. Passed the full design dialectic and three implementation tasks; caught only at final acceptance.
- **Failure class:** A field mutated by both sides of an authority/trust boundary but modeled as single-owned is silently incoherent — each task's slice looks locally correct, so it slips design review.
- **Lesson:** Add a split-authority design-smell check to `spec-plan-tasks`' plan stage: when one side produces a value and the other consumes or also mutates it across a trust boundary, pin the explicit reconciliation model (server-absolute vs. client-owned-with-server-deltas/ledger) before fan-out.
- **Scope:** shared.
- **Status:** promoted-to(spec-plan-tasks skill).

## 2026-07-02 — Multi-component milestones need an early end-to-end smoke, not just per-package green
- **Context:** Issue #44 (spacewars M2, #80) — server and client SDK were on incompatible protocol versions; every per-package unit suite stayed green through three tasks while every real client join was rejected. Surfaced only at final two-tab acceptance.
- **Failure class:** Components tested in isolation can all pass while the integration between them is broken; unit-green is not feature-working.
- **Lesson:** When a milestone spans a client↔server or other multi-component boundary, `spec-plan-tasks` decomposition must include an early cross-component integration-smoke task (two real endpoints exchanging state) before the big fan-out, and acceptance criteria must include a real end-to-end probe.
- **Scope:** shared.
- **Status:** promoted-to(spec-plan-tasks skill).

## 2026-07-02 — A test naming a security mechanism must be proven non-vacuous
- **Context:** Issue #43 (spacewars M3/T4, PR #92) — a `[SEC]` test claimed a specific removal call was load-bearing for evicting a collected entity from client state; mutation-testing it (commenting out the call) showed the test still passed, because the framework's map-level DELETE covered the path regardless. The entire dialectic blocker rested on an unverified framework assumption.
- **Failure class:** A test that names a mechanism as the thing preventing a failure can pass whether or not that mechanism runs — a vacuous guard giving false confidence, worst on `risk:security` work.
- **Lesson:** For any test asserting a specific mechanism prevents a failure (mandatory for `[SEC]`/`risk:security`), the reviewer verifies non-vacuity by disabling/mutating the mechanism and confirming the test fails. A design blocker resting on assumed framework behavior must be source- or spike-verified. Added to `review-checklist` and `red-team`.
- **Scope:** shared.
- **Status:** promoted-to(review-checklist skill, red-team skill).

## 2026-07-02 — Review verification must run every configured gate, not just tests+typecheck
- **Context:** Issue #42 (spacewars M2/M3, recurring twice) — two lint errors reached `main` because reviewers ran test+typecheck but not lint, despite lint being a repo-enforced gate. Both were trivially auto-fixable and slipped an otherwise-thorough cross-model review.
- **Failure class:** A reviewer's local verification omitting a gate the repo already enforces lets tooling-catchable defects reach `main` anyway.
- **Lesson:** `review-checklist`'s Tests section now requires running the repo's full configured verification set (typecheck + test + lint/format, whatever `package.json`/CI defines), treating a lint/format failure as at least a nit — blocking if already on `main`.
- **Scope:** shared.
- **Status:** promoted-to(review-checklist skill).

## 2026-07-02 — Self-verify after a multi-file edit is a per-role gap, not a one-time fix
- **Context:** Issue #28 — a `swarm:architect` round-2 dialectic revision hit a mid-write API disconnect; two of three critique fixes never landed, but all three files had fresh mtimes and looked complete. The 2026-06-30 cycle (PR #22) had already added a self-verify re-read step to `implementer.md` for the same class of failure, but the Architect — a second role that edits multiple artifacts per pass — still had no equivalent instruction, and it was the Architect that failed here.
- **Failure class:** A self-verification instruction added to one generator role does not generalize to other roles that share the same failure mode (multi-file edit, no post-write re-read). Each role needs the instruction stated explicitly; agents don't infer it across role boundaries.
- **Lesson:** When a self-verify / re-read-after-write step is added for one role, audit every other role that performs multi-file edits (Architect, Implementer, and any future generator) and add the same step there too, in the same cycle. Added to `architect.md`'s dialectic step (re-read spec/plan/tasks against the critique list before reporting convergence). Also added an explicit `crashed` run-log status (`run-log` skill + `swarm_log.py`) so an orchestrator that confirms an interruption can log it as an unambiguous terminal state rather than `done`/`blocked`.
- **Scope:** shared.
- **Status:** recurring (first instance: implementer.md, 2026-06-30 cycle; second instance: architect.md, this cycle — same class, different role).

## 2026-07-02 — Re-pin thrash: patch-level dependency bumps don't need their own proposal
- **Context:** Four `spec-plan-tasks` re-pin proposals in 6 days (#4 → v0.11.9, #21 → v0.12.1, #37 → v0.12.2, #39 → v0.12.3), none of which tripped the `revisit_if` or changed the wrapper — each was pure ledger churn on a fast-moving upstream (`spec-kit` ships near-daily).
- **Failure class:** The anti-thrash discipline in `scout.md`/`scout-scan` was written for *novel tool* thrash ("chase novelty") but didn't cover *re-pin* thrash on an already-adopted dependency — a different mechanism producing the same symptom (issue/PR overhead disproportionate to decision content).
- **Lesson:** Batch routine patch-level re-pins (no `revisit_if` signal, no wrapper change) to a weekly cadence; re-pin immediately only when a scan finds a `revisit_if`-relevant change or a minor/major bump. Hardened directly into `knowledge/scout-sources.md`'s scan discipline this cycle, given four recurrences before the fix.
- **Scope:** shared.
- **Status:** promoted-to(knowledge/scout-sources.md).

## 2026-06-27 — Pin upstream by release, never `@latest`
- **Context:** Scout finding #4 — `spec-plan-tasks` ledger row pinned `github/spec-kit@latest`. Spec Kit shipped 55+ releases and reached v0.11.9, tripping the `revisit_if` for native gates.
- **Failure class:** `adopt`/`adapt` rows pinned to a moving ref drift silently — behavior changes before it is vetted, defeating the divergence ledger.
- **Lesson:** Every `adopt`/`adapt` row carries a concrete `ref`/`sha`/tag (here: `@v0.11.9`); the Scout re-pins on each scan rather than relying on `@latest`. When a `revisit_if` trips, prefer **narrow the wrapper to our genuine value-add** (risk-aware lane mapping) over wholesale retire.
- **Scope:** shared.
- **Status:** recurring (confirmed 2026-06-30 scout cycle: re-pinned spec-kit @v0.11.9 → @v0.12.1 after verifying revisit_if not tripped).

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
