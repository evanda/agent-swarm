---
description: Install the swarm into a target project repo cloned alongside agent-swarm — merges into existing config, then guides credential setup.
argument-hint: <path-to-target-repo> [release-web|release-android]
disable-model-invocation: true
---

# /install — bootstrap the swarm into a project repo

Run from the **agent-swarm** repo, targeting another repo cloned in this
environment. You drive a deterministic installer, then apply judgment to the
fuzzy parts and walk the human through credentials.

**Target:** `$ARGUMENTS` (path to the project repo; optional cartridge).

## Steps

1. **Confirm the target.** Resolve the path. If it doesn't exist or isn't a git
   repo, stop and ask. Never target the agent-swarm repo itself.

2. **Dry-run first.** Run:
   ```
   python3 scripts/install.py <target> --cartridge <release-web|release-android> --dry-run
   ```
   Show the human the plan. The installer **merges** into existing
   `.claude/settings.json` and **injects a marked block** into an existing
   `CLAUDE.md` (it never clobbers; it backs up). Pick the cartridge from the
   project's stack if not given (web vs Android); ask if ambiguous.

3. **Apply.** Re-run without `--dry-run`. It will:
   - merge `extraKnownMarketplaces.swarm` + `enabledPlugins` into settings.json,
   - add/refresh the `<!-- BEGIN swarm -->…<!-- END swarm -->` block in CLAUDE.md,
   - create `.swarm/config.json` and `constitution.delta.md` if absent,
   - create `specs/` and `docs/decisions/`.

4. **Reconcile prose (judgment).** Read the target's resulting `CLAUDE.md`. If the
   project already had swarm guidance or conflicting conventions, tidy it so the
   file reads cleanly — but keep all edits to the swarm block between the markers,
   and leave the project's own content alone. Edit `constitution.delta.md` to
   capture any obvious repo-specific risk surfaces or stack rules you can infer.

5. **Credentials — walk the human through it; assume they know nothing.** Do NOT
   just point at a doc. Drive this as an interactive sub-flow. Background for you
   is in `docs/credentials.md`, but *you* deliver the steps.

   First, **check what already works** — don't make them create a token they don't
   need. Try a read then a write-scoped check against both repos (e.g. via the
   GitHub MCP `get_me`, and reading the target + `agent-swarm`). If the
   environment already has working GitHub access with the right scope, say so and
   skip to verification.

   If a token is needed, walk them through creating one, step by step:
   1. Tell them this single token needs to write to **two** repos — the target
      project (its work) and **agent-swarm** (so the swarm can file
      learning-proposals upstream). One token, two repos — not repo-to-repo access.
   2. Send them to **https://github.com/settings/tokens?type=beta** (fine-grained
      PAT). Walk the form:
      - **Resource owner:** the account/org owning both repos.
      - **Repository access:** "Only select repositories" → pick **the target
        repo AND `agent-swarm`**.
      - **Permissions:** Repository permissions → **Issues: Read and write**,
        **Pull requests: Read and write**, **Contents: Read and write**.
      - Set an expiry, click Generate, copy the token.
      (Classic PAT with `repo` scope works too if they prefer — mention it as the
      fallback.)
   3. **Inject it — never have them paste the value into chat or a committed file.**
      Pick the method for their environment and give the exact action:
      - **Anthropic cloud dev env (their default):** add `GITHUB_TOKEN` in the
        environment's variables/secrets (Settings for the environment on
        code.claude.com), then restart the session so it's in the env. The plugin
        `.mcp.json` reads `${GITHUB_TOKEN}`.
      - **Local CLI:** `export GITHUB_TOKEN=…` in their shell profile, or a
        gitignored `.claude/settings.local.json` `env` block.
   4. **Model auth:** tell them interactive `/swarm:*` needs **no**
      `ANTHROPIC_API_KEY` — their session covers it. The key is only for the
      central repo's nightly/weekly **workflows** (add as an Actions secret on
      agent-swarm). Mention it only if they ask about the loops.

   Then **verify the token actually works**: make a real call against both repos
   (read both; confirm write scope, e.g. list/permissions). Report pass/fail per
   repo and, on failure, name the most likely missing scope or unselected repo.

6. **Verify & hand off.** Tell them to: review the diff in the target repo,
   commit it there, run `/plugin install swarm@swarm` (project scope) +
   `/reload-plugins` from the target, and confirm dormancy (a plain `claude`
   session with no `/swarm:*` typed behaves normally). Offer to commit the target
   changes if they want.

Keep the human in the loop at the diff and at credentials — those are the two
places a mistake is costly. Don't end the command until GitHub access is verified
working against both repos (or the human explicitly defers it).
