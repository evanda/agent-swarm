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
  upstream: anthropics/pr-review-toolkit@1.0.0 (commit f7ab5c7, bundled 2025-10-09, unchanged since)
  delta: "Added our severity schema (blocker/concern/nit) + iterative loop. The prior pin (`v1.4.0`) did not correspond to any real tag for this plugin — `plugins/pr-review-toolkit/.claude-plugin/plugin.json` on `anthropics/claude-code@main` has read `1.0.0` since the single bundling commit, and history shows no other commits since. Likely transcribed from the wrong versioning scheme at adoption time (e.g. confused with a `claude-code` core release tag). Corrected 2026-07-08 after two independent scans confirmed it (#76, #78, #83)."
  revisit_if: "pr-review-toolkit adds native multi-round iteration → drop our wrapper."

- capability: lane-router
  posture: author
  upstream: null
  delta: "No external tool routes by our risk rubric."
  revisit_if: "An external risk-aware triage router appears."

- capability: spec-plan-tasks
  posture: adapt
  upstream: github/spec-kit@v0.12.7
  delta: "Wraps Spec Kit (constitution→specify→plan→tasks→clarify). v0.12.2 retired the Windsurf/iflow integrations and bounded fan-out max_concurrency; v0.12.3 was a maintenance/integration-hygiene patch; v0.12.4 (2026-07-02) adds Python script-type support, a private-repo release-asset URL fix, template-interpolation fixes, and label-driven bug-fix/bug-test agentic workflows; v0.12.5 (2026-07-06) is workflow-validation hygiene (gate reject-option case-insensitivity, lexicographic string-comparison fixes); v0.12.6 (2026-07-07) adds catalog URL validation (HTTPS-only), extension script-path fixes, and config-manager coercion for non-mapping YAML roots; v0.12.7 (2026-07-07) is bundle-update fixes plus more workflow-validation and integration env-var handling — still maintenance/plumbing throughout. Our wrapper stays narrowed to risk-aware lane mapping (lane:* × risk:*) on top of their phase gates — the revisit_if trigger (native risk-aware gating) was not tripped by any release through v0.12.7; the `gate` entries in its changelog remain a generic, manually-authored approval-checkpoint step type, not a built-in risk classifier."
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
  delta: "We own the Orchestrator: /swarm:start fan-out to role agents, swarm_log.py run-log for cross-session durability + resume (resume-cycle), and adversarial gates (dialectic/red-team/independent reviewer). Dynamic Workflows (Claude Code >= v2.1.154) confirmed GA as of late June 2026 (code.claude.com/docs/en/workflows carries no preview label; press coverage corroborates) — condition 1 of revisit_if (preview graduation) is now fully met. Condition 2 (cross-session-durable resume) is still NOT met per the current docs: 'Resume works within the same Claude Code session. If you exit Claude Code while a workflow is running, the next session starts the workflow fresh.' No posture change. Separately, Claude Code shipped **Agent Teams** (~v2.1.178-v2.1.199): peer-to-peer multi-agent coordination — named teammates as full independent sessions, a shared dependency-blocking/file-locked task list, direct inter-agent messaging, reusable subagent-definitions-as-teammates, and quality-gate hooks (TeammateIdle/TaskCreated/TaskCompleted). Structurally closer to our role/coordination model than Dynamic Workflows' script-driven fan-out, but explicitly experimental/disabled-by-default with no session-resume for teammates, no nested teams, and lagging task-status sync — Watch only, no ledger posture change, no adapt spike."
  revisit_if: "Dynamic Workflows exits research preview with a stable scripting API AND supports cross-session-durable resume → spike adapting /swarm:start's fan-out onto it while keeping our role/lane/gate semantics + run-log; downgrade this row to `adapt`. Separately: Agent Teams exits experimental/flag-gated status AND adds session-resume for in-process teammates AND reliable task-status sync → spike adapting the Orchestrator's role coordination onto it while keeping our lane/gate semantics + run-log."
```
