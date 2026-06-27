# 0001. Initial swarm build from the master spec

- **Status:** accepted
- **Date:** 2026-06-27
- **Issue/PR:** initial scaffolding on `claude/swarm-master-build-infra-2gt06c`
- **Deciders:** Evanda (human), build agent

## Context

`swarm-master-build-spec.md` is the single source of truth for the dev swarm. It
describes a central `org/swarm` repo that is simultaneously a marketplace, a
plugin, and a knowledge base, built in the order of §13. This ADR records the
non-obvious decisions made while scaffolding it, so future readers know *why*.

## Decision

Build the full §5 layout in this repo (`evanda/agent-swarm`) across the §13
rungs that don't require a human action: the central skeleton, conventions +
routing, the review split, the Deep lane + dialectic, the paper trail + the
global guard hook, and both self-improvement loops, plus the cartridges and the
consumer footprint template.

## Rejected alternatives

- **Separate `swarm` repo distinct from `agent-swarm`.** Rejected: the spec's
  README designates this repo as the implementation target, and a single repo
  keeps the marketplace source path relative (`./plugins/swarm`), which the spec
  explicitly requires (private external sources aren't org-sync fetchable).
- **One large commit covering everything.** Followed the spec's "PR per logical
  unit" intent in spirit, but since this is the *initial* scaffold on a dedicated
  branch, it lands as one coherent skeleton; subsequent changes go through the
  reviewed-PR flow.

## Deviations from the spec (recorded for the ledger)

1. **`org/swarm` → `evanda/agent-swarm`.** The spec uses an `org/swarm`
   placeholder; we use the real repo slug in `plugin.json`, `.swarm/config.json`,
   the consumer `settings.json`, and the workflows.
2. **Model diversity for adversaries.** The spec requires each adversary to run
   on a *different model* than its generator (anti-collusion). Agent frontmatter
   carries a single sensible default model tier; the hard "different model"
   requirement is documented in `challenger.md` / `reviewer.md` and is intended
   to be enforced at dispatch via the Orchestrator's subagent model override
   (`CLAUDE_CODE_SUBAGENT_MODEL`). Frontmatter alone cannot express "not the
   same as the caller."
3. **Eval harness.** `knowledge/evals/run.py` runs a dependency-free *structural*
   validation by default (so `validate-plugin.yml` stays keyless) and exposes a
   `--llm` extension point for the live rubric check that `improver.yml` runs with
   a key. The live wiring is a marked TODO.
4. **Global hooks.** Per §6/§10 only the `PreToolUse` secrets/destructive-op
   guard is registered globally; all other automation stays inside swarm
   agents/skills so plain sessions remain 100% normal.

## Consequences

- The repo is swarm-ready. Remaining human-only rungs: activating a *real
  consumer repo* (§10A / rung 4), running an issue end-to-end, tagging `v0.1.0`
  so the consumer `settings.json` pin resolves, and adding the
  `ANTHROPIC_API_KEY` secret for the Improver/Scout jobs.
- `revisit_if` for the ledger: if Claude Code adds per-agent "different model
  than caller" frontmatter, drop the documented-convention workaround (deviation 2).
