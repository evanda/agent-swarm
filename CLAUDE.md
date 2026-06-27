# agent-swarm (the central `swarm` brain)

This repo is simultaneously the **marketplace**, the **plugin**, and the
**knowledge base** for the dev swarm. The complete design is
[`swarm-master-build-spec.md`](swarm-master-build-spec.md) — the single source of
truth.

## Map

- `plugins/swarm/` — the plugin: `agents/` (10 roles), `skills/` (methodology),
  `commands/` (entry points), `hooks/` (the one global guard), `.mcp.json`.
- `knowledge/` — `constitution.md` (always-on rules), `learnings.md`,
  `dependencies.md` (divergence ledger), `scout-sources.md`, `evals/`.
- `.github/workflows/` — `validate-plugin.yml` (CI), `improver.yml` (nightly
  inward), `scout.yml` (weekly outward).
- `templates/consumer/` — copy into an existing repo to activate the swarm (§10A).
- `scripts/` — `validate_plugin.py` (CI), `install.py` (bootstrap into a target
  repo), `swarm_log.py` (run-log + live checklist + debrief rendering).
- `docs/decisions/` — ADRs · `docs/debriefs/` — per-cycle reports (when committed).

## Conventions

- **The brain changes only via reviewed PRs.** Improver/Scout propose; a human
  merges. Bump `plugins/swarm/.claude-plugin/plugin.json` `version` on every
  meaningful change; consumers pin to it.
- **Entry commands are explicit-only** (`disable-model-invocation: true`) and
  operational skills are `user-invocable: false` — so the swarm installs dormant
  and nothing fires until a human types `/swarm:*`.
- Before any structural change, run `python3 scripts/validate_plugin.py` and
  `python3 knowledge/evals/run.py`.

The rules themselves live in [`knowledge/constitution.md`](knowledge/constitution.md);
methodology lives in the skills under `plugins/swarm/skills/`. Prefer pointing at
a skill over restating it here.
