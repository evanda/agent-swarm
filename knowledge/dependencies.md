# Divergence ledger

The watch-list that makes "replace DIY with best practice" tractable. One row
per capability the swarm depends on or owns. Maintained by the Scout (§8) and
reviewed on every relevant PR.

- **posture** ∈ `adopt` (use upstream as-is, pinned) · `adapt` (wrap/extend
  upstream) · `author` (we own it; no good external) · `retire` (slated for
  removal).
- Every **adapt/author** row MUST carry a `revisit_if` trigger.
- Every **adopt** row MUST carry an `upstream` pin (`ref`/`sha`/tag).
- Pin all upstream by `ref`/`sha` so nothing changes behavior until vetted.

```yaml
- capability: code-review
  posture: adapt
  upstream: anthropics/pr-review-toolkit@v1.4.0
  delta: "Added our severity schema (blocker/concern/nit) + iterative loop."
  revisit_if: "pr-review-toolkit adds native multi-round iteration → drop our wrapper."

- capability: lane-router
  posture: author
  upstream: null
  delta: "No external tool routes by our risk rubric."
  revisit_if: "An external risk-aware triage router appears."

- capability: spec-plan-tasks
  posture: adapt
  upstream: github/spec-kit@v0.11.9
  delta: "Wraps Spec Kit (constitution→specify→plan→tasks→clarify). Spec Kit now exposes native gate detail (run/resume --json, v0.11.4) and a hookable extension/preset model; our wrapper is narrowed to risk-aware lane mapping (lane:* × risk:*) on top of their phase gates."
  revisit_if: "Spec Kit ships native *risk-aware* gating that maps to our auth/data/money/destructive rubric → drop our lane-mapping layer."

- capability: feature-recon (Explorer)
  posture: adapt
  upstream: anthropics/claude-code:plugins/feature-dev@latest
  delta: "Seeded Explorer/Architect from feature-dev; trimmed to return distilled maps only."
  revisit_if: "feature-dev adds a read-only recon mode that returns condensed summaries."

- capability: skill-authoring
  posture: adopt
  upstream: skill-creator@claude-plugins-official
  delta: "Used as-is to author skills."
  revisit_if: "n/a — adopt; re-pin on upstream releases."

- capability: write-time-security-guard
  posture: adopt
  upstream: security-guidance@2.0.6 (claude-plugins-official; requires Claude Code >= v2.1.144)
  delta: "Complementary pre-tool hook covering ~25 dangerous write/edit patterns (eval/new Function, os.system, child_process.exec, pickle, DOM injection, hardcoded secrets). Our guard.py keeps swarm-specific invariants (rm -rf / protected-branch / worktree-escape / secret blocks); this provides the generic SAST floor we choose not to hand-roll. A safety floor beneath our bespoke guard, not a replacement."
  revisit_if: "n/a — adopt; re-pin on upstream releases. Reconsider if it gains config that conflicts with guard.py, or if its pattern bank starts to overlap our swarm invariants."

- capability: agent-orchestration
  posture: author
  upstream: null
  delta: "We own the Orchestrator: /swarm:start fan-out to role agents, swarm_log.py run-log for cross-session durability + resume (resume-cycle), and adversarial gates (dialectic/red-team/independent reviewer). Claude Code Dynamic Workflows (research preview 2026-05-28, requires v2.1.154+) now provides a native fan-out substrate (JS orchestration script, <=16 concurrent / 1000 total agents, same-session resume, adversarial cross-check pattern) covering the execution mechanics we hand-roll — but not our role/lane/gate semantics or cross-session-durable run-log."
  revisit_if: "Dynamic Workflows exits research preview with a stable scripting API AND supports cross-session-durable resume → spike adapting /swarm:start's fan-out onto it while keeping our role/lane/gate semantics + run-log; downgrade this row to `adapt`."
```
