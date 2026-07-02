# agent-swarm

A team of specialized AI agents that turn GitHub Issues into verified PRs. A
persistent **Orchestrator** reads an issue, routes it by risk into a lane, and
delegates to ephemeral subagents — each generator paired with an adversary on a
different model. GitHub is the control plane; the swarm installs **dormant** and
nothing fires until you type a `/swarm:*` command.

This repo is the central brain: the **marketplace**, the **plugin**, and the
**knowledge base**. Design & rationale: **[swarm-master-build-spec.md](swarm-master-build-spec.md)**
(with an Addendum of decisions since the build); ADRs in [`docs/decisions/`](docs/decisions/).

## The agents

| Agent | Job |
|---|---|
| **Orchestrator** | triage → route → decompose → delegate → synthesize (never writes code) |
| **Explorer** | read-only recon; returns a distilled map of the code |
| **Architect** | turns an ambiguous issue into spec → plan → tasks; records decisions |
| **Challenger** | attacks the spec before fan-out (different model than Architect) |
| **Implementer** | builds one task → one PR in its own worktree |
| **Reviewer** | independent verification of a PR (different model than Implementer) |
| **Integrator** | resolves conflicts, drives the merge queue |
| **Scribe** | paper trail: run log, ADRs, follow-up issues, learning-proposals |
| **Improver** | inward loop: retros/traces/evals → reviewed PRs (nightly) |
| **Scout** | outward loop: scans SOTA tooling → proposals (weekly) |

Work is routed into one of three lanes by a conservative risk rubric — **Express**
(trivial, reversible), **Standard** (clear, small design), **Deep** (ambiguous,
cross-cutting, or risk-flagged → spec + human gate). See the spec for the lane
table and the `risk:*` flags that force Deep.

## Commands

| Command | What it does |
|---|---|
| `/swarm:start <issue# \| description>` | triage, route, and run the lane — or, on an issue with prior state, resume that cycle from its frontier |
| `/swarm:express <description>` | force the cheap Express lane for a known-trivial fix |
| `/swarm:status [issue#]` | what each agent is doing now, gates, tokens, links |
| `/swarm:stop [issue#]` | gracefully halt a cycle (Esc interrupts agents; this cleans up) |
| `/swarm:retro [scope]` | retrospective → learning-proposals |
| `/swarm:help` | full in-tool reference |

You can also run work async: file/assign an Issue with the `swarm:async` label
and the scheduled job picks it up — no session needed. `lane:*`/`triage` are
routing/telemetry only and never themselves launch a run; see [async job-picker
contract](#async-job-picker-contract) below for what the scheduled job must do.

## Progress & debriefs

A swarm run is token-heavy and spreads work across opaque subagents, so every run
is instrumented:

- **Live checklist** — a single auto-updating comment on the issue, refreshed at
  each step; `/swarm:status` renders it on demand.
- **Debrief** — at cycle end the Scribe posts a comprehensive report (what each
  agent did, decisions, PRs, **token cost**, timeline) to the issue, and
  optionally commits it to `docs/debriefs/<issue#>.md` (`.swarm/config.json`
  `debrief`: `issue` | `commit` | `both`).

Both render from the same event log so they can't drift. Details: the `run-log`
and `debrief` skills.

## Async job-picker contract

The scheduled job that watches for `swarm:async` is external to this repo (a
Claude Code routine or Action you configure per-project) but must follow the
same safety properties as an interactive run — it is not a shortcut around
review:

1. **Explicit opt-in trigger only.** Watch for the `swarm:async` label, never
   bare `lane:*`/`triage` — those are routing/telemetry, stamped by an
   interactive run mid-flow, and must not silently launch a second, parallel
   build of the same issue.
2. **Claim before starting, skip if already claimed.** Check the issue for an
   existing `<!-- swarm:claim -->` comment or assignee before doing any work; if
   one is present from a different run, bail without touching the issue. If
   clear, post its own claim comment
   (`🐝 Swarm Orchestrator — async run started <!-- swarm:claim mode=async -->`)
   before proceeding.
3. **Never commit directly to a shared/integration branch.** Land the result
   through the identical Implementer→Reviewer→merge-queue path every other
   swarm path uses — a feature branch, an independent reviewer on a different
   model, then the merge queue. No exceptions for "it's just a scheduled job."

Minimal routine prompt for the scheduled session:

```
You are running the async swarm picker in a checkout of this project. For each
open issue labeled `swarm:async`:

1. Check for an existing swarm claim comment or assignee. If one exists from a
   different run, skip this issue entirely.
2. Post a claim comment, then act as the Orchestrator (see
   plugins/swarm/agents/orchestrator.md) — triage, route, and run the lane.
3. Never commit directly to a shared/integration branch. Always open a PR
   reviewed by an independent agent on a different model, per the normal
   Implementer -> Reviewer -> merge-queue path.

Report a one-paragraph summary per issue processed (or skipped, and why).
```

## Bootstrapping a project

Clone the target project alongside this repo, then from a Claude Code session in
agent-swarm run:

```
/install <path-to-target-repo>
```

It writes a tiny footprint into the target (merging into any existing `CLAUDE.md`
/ `.claude/settings.json`, never overwriting), then walks you through the GitHub
token setup and verifies it. The target only **references** the central plugin at
a pinned ref — it never copies the agents/skills, so it can't go stale, and a
running app session needs no second clone. Adopt central improvements by bumping
the pin.

Then, in a Claude Code session **in the target repo**, activate the plugin:

```
/plugin install swarm@swarm     # choose "project" scope
/reload-plugins
```

The repo is now swarm-ready but dormant — nothing fires until a human types
`/swarm:*`.

→ **Deeper:** [credentials & access model](docs/credentials.md) ·
[consumer footprint](templates/consumer/README.md) ·
[install vs runtime boundary](docs/decisions/0003-install-vs-runtime-boundary.md)

## Self-improvement

The brain changes only via **reviewed PRs**: the Improver (inward) and Scout
(outward) file `learning-proposal` issues; a human merges. Bump
`plugins/swarm/.claude-plugin/plugin.json` `version` on every meaningful change.

**Running the loops on your subscription (no API credits).** A Claude Max/Pro
subscription doesn't include Anthropic API access, so the loops can run three ways
— pick one:

- **Claude routine (recommended if you have Max):** schedule a Claude Code session
  that runs `/swarm:improve` and `/swarm:scout`. These execute the loops in-session
  on your subscription — no API key, no Actions.
- **GitHub Actions on your subscription:** run `claude setup-token` once, add the
  output as the repo secret `CLAUDE_CODE_OAUTH_TOKEN`; `improver.yml`/`scout.yml`
  then run on schedule against your subscription.
- **GitHub Actions on the API:** set the `ANTHROPIC_API_KEY` secret instead
  (pay-as-you-go API billing) and swap it back into the workflow `env`.

**Routine prompt (no install needed).** A scheduled session runs inside a checkout
of this repo, so the role instructions are already present as files — the routine
doesn't need the plugin installed; it can point Claude straight at them. Use this
prompt to run both loops nightly in one job (scout first, so the Improver has
proposals to act on):

```
You are running in a checkout of the agent-swarm repo. Run its self-improvement
loops in order, and merge nothing:

1. Act as the Scout — follow plugins/swarm/agents/scout.md and the scout-scan /
   eval-dependency skills: scan knowledge/scout-sources.md and the revisit_if
   triggers in knowledge/dependencies.md, score findings (default Watch), and file
   Adopt/Adapt/Retire findings as `external` learning-proposal issues.

2. Then act as the Improver — follow plugins/swarm/agents/improver.md: process the
   open learning-proposal issues, apply the smallest correct edits, run
   `python3 knowledge/evals/run.py --llm` and confirm NO regression, and open ONE
   PR labeled `meta`. Do not merge it.

Finish with a one-paragraph summary (issues filed, PR link, eval result).
```

(Installing the plugin is only needed if you want the `/swarm:scout` /
`/swarm:improve` slash commands interactively — load it with
`/plugin marketplace add <path-to-this-repo>` → `/plugin install swarm@swarm` →
`/reload-plugins`. The routine above works without it.)

## Repo layout & contributing

```
plugins/swarm/   agents · skills · commands · hooks · scripts (runtime) · .mcp.json
knowledge/       constitution · learnings · dependencies (ledger) · scout-sources · evals
scripts/         setup/CI tools (install.py, validate_plugin.py)
docs/            decisions (ADRs) · debriefs · credentials.md
templates/       consumer footprint
```

Before any structural change: `python3 scripts/validate_plugin.py` and
`python3 knowledge/evals/run.py`. Conventions live in [CLAUDE.md](CLAUDE.md).

## Operator setup (one-time)

- Releases are automatic: bump `plugin.json` `version` **and** the consumer
  template `ref` in the same PR (CI enforces they match); on merge,
  `release.yml` tags `vX.Y.Z` and publishes the GitHub release so consumers'
  pinned `ref` resolves.
- Decide how the Improver/Scout loops run (see *Self-improvement* above): a
  scheduled Claude routine (`/swarm:improve`, `/swarm:scout`) on your
  subscription, or the Actions workflows with `CLAUDE_CODE_OAUTH_TOKEN`
  (subscription) or `ANTHROPIC_API_KEY` (API).
