# agent-swarm (the central `swarm` brain)

This repo is simultaneously the **marketplace**, the **plugin**, and the
**knowledge base** for the dev swarm. The original design and rationale is
[`swarm-master-build-spec.md`](swarm-master-build-spec.md) (see its Addendum +
[`docs/decisions/`](docs/decisions/) for decisions since); day-to-day usage lives
in the [README](README.md).

## Map

- `plugins/swarm/` — the plugin: `agents/` (10 roles), `skills/` (methodology),
  `commands/` (entry points), `hooks/` (the global guard, `PreToolUse`; plus an
  advisory version-check nudge on `/swarm:*` prompts, `UserPromptSubmit`),
  `.mcp.json`, `scripts/` (runtime tools shipped to consumers, e.g. `swarm_log.py`).
- `knowledge/` — `constitution.md` (always-on rules), `learnings.md`,
  `dependencies.md` (divergence ledger), `scout-sources.md`, `evals/`.
- `.github/workflows/` — `validate-plugin.yml` (CI), `improver.yml` (nightly
  inward), `scout.yml` (weekly outward).
- `templates/consumer/` — copy into an existing repo to activate the swarm (§10A).
- `scripts/` — central/setup-only tools (NOT shipped to consumers):
  `validate_plugin.py` (CI), `install.py` (one-time bootstrap into a target repo,
  assumes both repos cloned). Runtime tools live in `plugins/swarm/scripts/`.
- `docs/decisions/` — ADRs · `docs/debriefs/` — per-cycle reports (when committed).

## Conventions

- **The brain changes only via reviewed PRs.** Improver/Scout propose; a human
  merges. On every meaningful change run `python3 scripts/bump_version.py`
  (`--minor`/`--major` as needed) — it bumps `plugin.json` `version` **and** the
  consumer template `ref` together. Never hand-edit either: CI rejects a PR
  where they drift, and merging auto-tags + publishes the release.
- **Entry commands are explicit-only** (`disable-model-invocation: true`) and
  operational skills are `user-invocable: false` — so the swarm installs dormant
  and nothing fires until a human types `/swarm:*`.
- Before any structural change, run `python3 scripts/validate_plugin.py` and
  `python3 knowledge/evals/run.py`.

The rules themselves live in [`knowledge/constitution.md`](knowledge/constitution.md);
methodology lives in the skills under `plugins/swarm/skills/`. Prefer pointing at
a skill over restating it here.
