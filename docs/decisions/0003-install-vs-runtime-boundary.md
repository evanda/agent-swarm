# 0003. Install-time vs runtime: reference, not copy

- **Status:** accepted
- **Date:** 2026-06-27
- **Issue/PR:** observability/bootstrap work on `claude/swarm-master-build-infra-2gt06c`
- **Deciders:** Evanda (human), build agent

## Context

Activating the swarm in an app repo could either **vendor** (copy all agents/
skills/hooks into the app) or **reference** the central repo. Vendoring goes
stale — apps activated long ago never see central improvements. Referencing risks
needing the central repo present wherever the app is worked on, and Anthropic
cloud dev environments are effectively single-repo (a session is tied to one
clone). We need central improvements to flow to consumers without assuming a
second clone at runtime.

## Decision

**Reference, pinned — never vendor.** A consumer commits only a tiny footprint
(`.claude/settings.json` with the marketplace at a pinned git `ref`,
`.swarm/config.json`, a `CLAUDE.md` block, `constitution.delta.md`). Claude Code
fetches the plugin from GitHub at that `ref` into its own plugin cache
(`~/.claude/plugins/cache/...`); the agents/skills/hooks are never copied into the
app. Bumping the `ref` is the adoption boundary (spec §12).

Draw a hard line between two phases:

- **Install (one-time, may assume both repos cloned).** `scripts/install.py` +
  the repo-local `/install <target>` run from an agent-swarm working copy against
  a sibling target. These are setup tools and stay in the central `scripts/` dir;
  they are **not** shipped to consumers.
- **Runtime (every app session, must NOT assume agent-swarm is cloned).** Anything
  a swarm agent invokes while working in the app repo must live **inside the
  plugin** (`plugins/swarm/scripts/`) and be referenced via `${CLAUDE_PLUGIN_ROOT}`,
  because that is what gets fetched into the consumer's plugin cache. The hook
  (`plugins/swarm/hooks/guard.py`) and the run-log/debrief renderer
  (`plugins/swarm/scripts/swarm_log.py`) follow this rule.

## Rejected alternatives

- **Vendor the whole plugin into each app.** Rejected: stale by construction; the
  whole point of the central brain is that improvements propagate. (If a consumer
  ever needs to pin-and-own a single skill, the spec's §9 vendoring-of-one-skill
  escape hatch applies — recorded in the ledger — not a blanket copy.)
- **Keep runtime helpers in the central `scripts/` dir.** Rejected (this was a
  latent bug): only the plugin directory is fetched to the consumer cache, so
  `scripts/swarm_log.py` would be absent at runtime. Moved into the plugin.
- **Require agent-swarm cloned alongside every app.** Rejected: cloud dev
  environments are single-repo; referencing via the plugin cache removes the need.

## Consequences

- Consumers get central improvements by bumping one pin; no app carries stale
  swarm code, and no app session needs a second clone.
- Rule for contributors: **setup tooling → `scripts/`; anything used during a
  swarm run → `plugins/swarm/scripts/` and invoked via `${CLAUDE_PLUGIN_ROOT}`.**
- `revisit_if`: if the run log ever needs to be written somewhere other than the
  working repo, keep it pointed at the repo (`--file`), never the read-only plugin
  cache.
