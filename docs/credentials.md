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

## Central repo automation (improver.yml / scout.yml)

These run in GitHub Actions on `agent-swarm`:

- `ANTHROPIC_API_KEY` — add as a repo **secret** (Settings → Secrets and
  variables → Actions).
- `GITHUB_TOKEN` — the Actions-provided token already has write on its own repo,
  which is all the Improver/Scout need (they operate within `agent-swarm`).

## Quick checklist

- [ ] Fine-grained PAT scoped to **target repo + agent-swarm** (Issues RW, PRs RW, Contents RW).
- [ ] Export it as `GITHUB_TOKEN` in your dev environment (or rely on the cloud harness's GitHub integration).
- [ ] Interactive use needs **no** `ANTHROPIC_API_KEY`.
- [ ] For the nightly/weekly loops: add `ANTHROPIC_API_KEY` as a secret on `agent-swarm`.
- [ ] Never paste secret values into chat, `CLAUDE.md`, or committed `settings.json`.
