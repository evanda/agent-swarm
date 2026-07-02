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

## 2026-07-02 — "Real-time observability" doesn't require a web app when the durable record is already a flat event log
- **Context:** Issue #29 — the ask was ambient, no-poll visibility into an in-flight run (one lane per role, live status) instead of repeatedly re-running `/swarm:status`. Framed as "swimlane visualizer," it read like a UI build (Canvas/SVG widget, a server, live wiring) — out of scope for a scaffolding-doc edit and deferred by two prior Improver cycles for that reason.
- **Failure class:** The ask's *name* implied more infrastructure than the ask's *substance* needed — every event the visualizer would render already lives in a flat, already-instrumented local file (`.swarm/run-log.jsonl`); the gap was a redraw loop, not a new architecture.
- **Lesson:** Implemented the ambient view as a terminal swimlane: `swarm_log.py watch --cycle N` polls the log and redraws one row per role (icon + current item + status), exiting at `cycle_completed`; `--once` gives a static render for scripting. No new dependency, no server — a human runs it in a side terminal instead of polling `/swarm:status`. `render_swimlane` is a pure function of the event list (same pattern as `checklist`/`debrief`), directly testable.
- **Scope:** shared.
- **Status:** promoted-to(swarm_log.py, run-log skill, help.md, status.md, README.md). A richer in-Claude-Code widget (if ever wanted) can build on the same `render_swimlane`/event data without redoing the instrumentation question.

## 2026-07-02 — "Reattach a crashed agent" means a fresh cattle instance inheriting committed state, not a process resume
- **Context:** Issue #16/#27 — a process restart killed a background Implementer mid-task, leaving ~90%-done work uncommitted in its worktree, indistinguishable from abandoned. The proposed fixes ("checkpoint/commit WIP", "resume-from-journal/reattach") implicitly asked for literal process resume, which the swarm's cattle-not-pets agent model doesn't support and the harness doesn't expose.
- **Failure class:** A recovery ask framed around resuming the dead thing (the process) obscures the actually-available recovery path (a fresh instance inheriting the dead one's on-disk state) — and without a committed checkpoint, "on-disk state" is uncommitted limbo that can't be trusted or cleanly handed off.
- **Lesson:** Implementer now commits WIP checkpoints (`wip: <state>`) after each coherent chunk of multi-file work, squashed before the final PR — a crash then leaves a committed recovery boundary. `resume-cycle` now states explicitly that "reattach" *is* fresh-Implementer-inherits-worktree (already the cattle model), and that inherited uncommitted changes get the same crashed-status suspicion as a confirmed crash until verified against spec/critique.
- **Scope:** shared.
- **Status:** promoted-to(implementer.md, resume-cycle skill).

## 2026-07-02 — Deep-lane ceremony should be right-sized per task and pipelined, not uniform and serial
- **Context:** Issue #20 — a correct 12-task Deep-lane run (~2.11M tokens, 34 agent-runs) took far too long: every task, even a 1–3 line UX tweak on already-reviewed code, paid the full lifecycle (worktree → implement → CI `--watch` → different-model review → merge → sync), and the critical path was mostly-serial with genuine parallelism the exception.
- **Failure class:** Two compounding causes — (1) the cycle-level lane was treated as uniform per-task ceremony instead of a design/gate-level setting, so trivial follow-ups paid full Deep review depth; (2) the Orchestrator barriered on each task's review/CI before dispatching the next independent task instead of pipelining, turning parallelizable work into a serial chain.
- **Lesson:** A Deep cycle's lane sets the *design* dialectic and human spec gate; per-task review depth still follows `route-issue`'s table applied to that task in isolation — a trivial single-component follow-up gets Express/Standard review, never a full Deep round, and never less than Express's single pass. Separately: dispatch the next independent task as soon as unblocked, hand a returned PR to review immediately, and enqueue-and-continue rather than synchronously polling CI — serialize only on genuine dependencies and human gates. (Micro-task batching and minimizing the serial spine were already covered by an earlier `spec-plan-tasks` fix; model-tiering by #47.)
- **Scope:** shared.
- **Status:** promoted-to(orchestrator.md).

## 2026-07-02 — A reconcile step this consequential needs enforced code, not just model-followed instructions
- **Context:** Issue #11 — `resume-cycle`'s Step 2/3 (reconcile against ground truth, compute the frontier) was prose the Orchestrator was trusted to follow correctly under messy real state (a merged-but-unlogged PR, a half-claimed sub-issue, a missing log on a different machine) — nothing verified the resulting frontier was actually correct.
- **Failure class:** A judgment call with a large blast radius (mis-judging the frontier can redo already-shipped work or silently skip a crashed task) left entirely to model-followed prose has no regression signal — a future skill edit could quietly break the reconcile logic and nothing would catch it before a live resume did.
- **Lesson:** Added `compute_frontier` to `swarm_log.py` (`frontier` subcommand) — a deterministic, testable function that computes each task's next stage (done/resume/dispatch/crashed) from the log, reconciled against ground truth. Wired two `knowledge/evals/resume/` fixtures (interrupted mid-review, crashed mid-write) into `run.py`'s always-on structural check (no API key needed) asserting the exact expected frontier — confirmed non-vacuous by mutating the function and watching the eval fail. `resume-cycle` Step 3 now calls this as the starting point rather than re-deriving it by hand.
- **Scope:** shared.
- **Status:** promoted-to(swarm_log.py, resume-cycle skill, knowledge/evals/resume/). Per the issue's own acceptance criteria, watch the first live resume before considering this fully proven — the fixtures cover the states we've seen, not necessarily every messy-real-world shape.

## 2026-07-02 — A degraded runtime must be a visible signal, not a silent fallback
- **Context:** Issue #27 — a process restart mid-Deep-lane-run dropped the swarm plugin/MCP connection; branded `swarm:*` agent types and the GitHub MCP became unavailable, and the run silently continued on `general-purpose` agents + the `gh` CLI, losing the Scribe/Integrator roles for the rest of the run. The downgrade was discovered via a tool-not-found error, not signalled.
- **Failure class:** When a capability the run depends on silently disappears (here: harness-level plugin/MCP reconnect after restart, outside this repo's control), continuing on a degraded fallback without surfacing that fact turns an infrastructure hiccup into an undetected scope/quality gap.
- **Lesson:** `resume-cycle` now runs a Step 0 check — confirm branded agent types and required MCPs resolve before rehydrating cycle state; if either is missing, log an explicit `note` ("swarm context degraded") and tell the human, rather than silently falling back. Auto-reconnect itself is a harness capability this repo doesn't own and can't fix directly; persisting/reattaching in-flight background agents across a restart remains open (overlaps #16).
- **Scope:** shared.
- **Status:** promoted-to(resume-cycle skill).

## 2026-07-02 — Worktree provisioning needs a documented per-project recipe, not per-agent rediscovery
- **Context:** Issue #30 (framework-level, split from a bub-specific companion) — Implementers in fresh `git worktree`s repeatedly hit missing-dependency walls (no `node_modules`, no generated assets, wrong toolchain version) and had to symlink the main checkout by hand each time, weakening the "verify in your own worktree" discipline.
- **Failure class:** A generic framework gap (worktrees aren't provisioned) has a project-specific fix (what to symlink, which toolchain) — solving it purely at the framework layer is impossible without the concrete recipe, and solving it purely per-agent means every Implementer rediscovers the same fix.
- **Lesson:** Added a **Worktree provisioning** section to the consumer `constitution.delta.md` template — a place to record the concrete recipe once (symlink targets, pinned toolchain, one-time build steps). The Implementer now checks it before running tests/build, and if empty, works out the fix and records it there via the Scribe so later worktrees don't repeat the discovery.
- **Scope:** shared (the contract/template) + project (the concrete recipe each project fills in) — a split case per `promote-learning`.
- **Status:** promoted-to(implementer.md, templates/consumer/constitution.delta.md).

## 2026-07-02 — WHERE-routing must gate every issue filing, not just learning-proposals
- **Context:** Issue #31 — the Scribe's follow-up-issue-filing responsibility defaulted to the active working repo with no WHERE check, while the sibling learning-proposal responsibility already used the `promote-learning` litmus. During the bub #187 run this put four framework-level `swarm:infra` issues onto the project repo instead of the shared swarm repo; they had to be transferred by hand (became agent-swarm#26–#30), and a combined issue had to be split into a portable contract + a project-specific recipe after the fact.
- **Failure class:** A routing discipline defined for one output type (learning-proposals) doesn't automatically apply to a sibling output type (follow-up issues) that shares the same underlying WHERE question — each output path needs the gate stated explicitly, not inferred by analogy.
- **Lesson:** Scribe's follow-up-issue step now runs the same `promote-learning` WHERE litmus before filing (portable → shared swarm repo with label existence confirmed; project-specific → project repo; mixed → two cross-linked issues), and records which repo each issue landed on and why.
- **Scope:** shared.
- **Status:** promoted-to(scribe.md).

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
