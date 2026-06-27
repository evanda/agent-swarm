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

## Using the swarm in another repo → `/install`

Clone the target project alongside this repo, then **from a Claude Code session
in agent-swarm, run:**

```
/install <path-to-target-repo>
```

That's the whole bootstrap. `/install` lays down the footprint, **merges** into
the target's existing `CLAUDE.md` / `.claude/settings.json` (never overwrites,
backs up, idempotent), reconciles the prose, and then **walks you through
creating and injecting the GitHub token step by step** and verifies it works —
you don't need to read any docs first.

The swarm installs **dormant**: nothing fires until a human types a `/swarm:*`
command.

<details>
<summary>Running the installer without Claude (plain script)</summary>

```bash
python3 scripts/install.py <path-to-target-repo> --dry-run   # preview
python3 scripts/install.py <path-to-target-repo>             # apply
```

This does the file merge but not the guided credential walkthrough. The access
model and manual token steps are in [`docs/credentials.md`](docs/credentials.md);
`templates/consumer/` is the raw footprint / manual fallback.
</details>

## Observability — progress & debriefs

A swarm run is token-heavy and runs work across many opaque subagents, so every
run is instrumented and rendered into two human views:

- **Live checklist** — agents emit structured events to `.swarm/run-log.jsonl`;
  the Scribe mirrors a rendered checklist into a single, edited GitHub issue
  comment, refreshed at each boundary. `/swarm:status <issue#>` renders it on
  demand. You see which subagent is doing what, dialectic rounds, gates, PRs, and
  tokens burned — without reading every subagent.
- **Debrief** — at cycle end the Scribe produces a comprehensive report (what each
  agent did, decisions + rejected alternatives, gates, PRs, token cost, candidate
  learnings, full timeline), posted to the issue and optionally committed to
  `docs/debriefs/<issue#>.md`. Configure via `.swarm/config.json` `debrief`
  (`issue` | `commit` | `both`, default `issue`). It's the best onboarding artifact
  for a new user and a primary input to the self-improvement loop.

Both views render from the same event log via `plugins/swarm/scripts/swarm_log.py`
— which **ships inside the plugin**, so it's present at runtime in any activated
repo without cloning agent-swarm. See the `run-log` and `debrief` skills.

## Self-improvement

The brain changes only via **reviewed PRs**. The **Improver** (inward: retros,
traces, evals) and **Scout** (outward: SOTA tooling) propose changes into a
`learning-proposal` queue; a human merges. Bump
`plugins/swarm/.claude-plugin/plugin.json` `version` on every meaningful change.

## Operator follow-ups (human-only)

- Tag `v0.1.0` so the consumer `settings.json` pin resolves.
- Add the `ANTHROPIC_API_KEY` repo secret for the Improver/Scout workflows.
- Activate a first real consumer repo and run an issue through end-to-end.
