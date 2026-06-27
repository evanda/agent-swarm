# agent-swarm

The central **`swarm`** brain — marketplace, plugin, and knowledge base for an
SWE agent swarm. A persistent Orchestrator reads work from GitHub Issues, routes
each item into one of three risk-based lanes, and delegates to ephemeral,
single-purpose subagents — each paired with an adversary on a different model.
GitHub itself is the control plane.

The complete design and build order live in
**[swarm-master-build-spec.md](swarm-master-build-spec.md)** — the single source
of truth.

## What's here

```
.claude-plugin/marketplace.json   # catalog
plugins/swarm/                     # the plugin
  agents/                          # 10 role agents (orchestrator, explorer, …)
  skills/                          # methodology (route-issue, dialectic, …)
  commands/                        # entry points (/swarm:start|express|retro)
  hooks/                           # the one global guard hook
  .mcp.json                        # shared MCP defaults (github)
knowledge/                         # constitution, learnings, ledger, sources, evals
.github/workflows/                 # validate-plugin (CI), improver (nightly), scout (weekly)
templates/consumer/                # copy into a repo to activate the swarm (dormant)
scripts/validate_plugin.py         # structural validator (run before changes)
docs/decisions/                    # ADRs
```

## Quick checks

```bash
python3 scripts/validate_plugin.py     # marketplace + plugin structure
python3 knowledge/evals/run.py         # golden evals (structural)
```

## Using the swarm in another repo

Copy `templates/consumer/` into a project and follow its README (§10A of the
spec). The swarm installs **dormant**: nothing fires until a human types a
`/swarm:*` command.

## Self-improvement

The brain changes only via **reviewed PRs**. The **Improver** (inward: retros,
traces, evals) and **Scout** (outward: SOTA tooling) propose changes into a
`learning-proposal` queue; a human merges. Bump
`plugins/swarm/.claude-plugin/plugin.json` `version` on every meaningful change.

## Operator follow-ups (human-only)

- Tag `v0.1.0` so the consumer `settings.json` pin resolves.
- Add the `ANTHROPIC_API_KEY` repo secret for the Improver/Scout workflows.
- Activate a first real consumer repo and run an issue through end-to-end.
