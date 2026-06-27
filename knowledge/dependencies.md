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
```
