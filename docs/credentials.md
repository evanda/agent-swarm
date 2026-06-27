# Credentials & access model

Who needs which key, and which direction access flows. The short version: **there
is no repo-to-repo trust relationship.** The only thing that matters is the
credential present in whatever environment is *running* the swarm.

## Two credentials

| Credential | What it's for | Who needs it |
|---|---|---|
| **Claude model auth** | running the agents | the *session/runner*. Interactive Claude Code (incl. Anthropic cloud dev envs) uses your existing login — **no `ANTHROPIC_API_KEY` needed**. Only the central repo's **scheduled workflows** (improver/scout) need `ANTHROPIC_API_KEY`, because they run headless. |
| **GitHub token** | reading/writing Issues & PRs (the control plane) | the environment running the swarm, via `GITHUB_TOKEN`. |

## Access direction (the question that trips people up)

When you run the swarm **inside a target project**, its GitHub token needs write
access to **both**:

1. the **target repo** — `issues:write` + `pull-requests:write` (+ `contents`
   for repo-local fixes), and
2. the **central `agent-swarm` repo** — `issues:write`, so the Scribe/Improver
   can file `learning-proposal` issues upstream.

```
            running the swarm in <target>
                       │
         GITHUB_TOKEN  │  needs write on BOTH
            ┌──────────┴──────────┐
            ▼                     ▼
       <target repo>        evanda/agent-swarm
      (issues + PRs)       (learning-proposals)
```

`agent-swarm` does **not** need any access to the target repo. It's not
"give repo A access to repo B" — it's "give the *token in your environment* scope
on the repos it will write to."

A single **fine-grained PAT** scoped to both repos (Issues: RW, Pull requests:
RW, Contents: RW) is the simplest setup. A classic PAT with `repo` works too.

## Anthropic cloud dev environments (your default)

- **Model auth:** handled by your Claude Code session — nothing to inject for
  interactive `/swarm:*` use.
- **GitHub:** the cloud harness often already provides GitHub integration. If you
  need the plugin's GitHub MCP (or run anything headless), inject the token as an
  **environment variable** in the environment's configuration:
  ```
  GITHUB_TOKEN = <fine-grained PAT with the scopes above>
  ```
  The plugin's `.mcp.json` passes `${GITHUB_TOKEN}` to the GitHub MCP server.
  See https://code.claude.com/docs/en/claude-code-on-the-web for where the
  environment's env vars / setup script are configured.
- **Never** commit a token value. For a machine-local override use a gitignored
  `.claude/settings.local.json` `env` block; for cloud, use the environment's
  secret/variable store.

## The self-improvement loops (Improver / Scout)

A Claude Max/Pro **subscription does not include Anthropic API access** — the API
is a separate, pay-as-you-go product. So the loops can run three ways; pick one:

1. **Claude routine on your subscription (no key, no Actions).** Schedule a Claude
   Code session that runs `/swarm:improve` and `/swarm:scout`. They execute
   in-session on your subscription. Simplest if you have Max and no API budget.
2. **GitHub Actions on your subscription.** Run `claude setup-token` once (mints a
   ~1-year token), add it as the `agent-swarm` repo secret
   `CLAUDE_CODE_OAUTH_TOKEN`. `improver.yml`/`scout.yml` already read it. CI runs
   draw on your subscription limits (same pool as interactive use).
3. **GitHub Actions on the API.** Add `ANTHROPIC_API_KEY` as the repo secret and
   swap it into the workflow `env` (replacing `CLAUDE_CODE_OAUTH_TOKEN`). Bills
   per-token to your Console org.

For the Actions paths, `GITHUB_TOKEN` is the Actions-provided token, which already
has write on its own repo — all the Improver/Scout need (they operate within
`agent-swarm`). Note: triggering the Actions from a routine does **not** avoid the
auth requirement — the job still runs Claude on the runner, so it needs option 2
or 3 configured. Option 1 is the only one that runs the model in your session.

## Quick checklist

- [ ] Fine-grained PAT scoped to **target repo + agent-swarm** (Issues RW, PRs RW, Contents RW).
- [ ] Export it as `GITHUB_TOKEN` in your dev environment (or rely on the cloud harness's GitHub integration).
- [ ] Interactive use (incl. `/swarm:improve` / `/swarm:scout`) needs **no** API key — your subscription covers it.
- [ ] For the loops, pick one: a scheduled Claude routine, or Actions with `CLAUDE_CODE_OAUTH_TOKEN` (subscription), or `ANTHROPIC_API_KEY` (API).
- [ ] Never paste secret values into chat, `CLAUDE.md`, or committed `settings.json`.
