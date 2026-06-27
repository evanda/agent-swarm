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

5. **Credentials (guide the human).** Read `docs/credentials.md` and give the
   human the *specific* actions for their setup. Decide which case applies:
   - **Anthropic cloud dev env (their default):** model auth is the session — no
     `ANTHROPIC_API_KEY` needed interactively. They need a GitHub token exported
     as `GITHUB_TOKEN` (env var/secret on the environment) with **issues + PR
     write on BOTH the target repo and the central agent-swarm repo** (the swarm
     files learning-proposals upstream). Note that the cloud harness may already
     provide GitHub access.
   - **Central repo automation (improver/scout):** `ANTHROPIC_API_KEY` secret on
     agent-swarm; the Actions-provided `GITHUB_TOKEN` covers same-repo writes.
   Spell out exactly where to paste each, and don't ask them to paste secret
   values into chat or committed files.

6. **Verify & hand off.** Tell them to: review the diff in the target repo,
   commit it there, run `/plugin install swarm@swarm` (project scope) +
   `/reload-plugins` from the target, and confirm dormancy (a plain `claude`
   session with no `/swarm:*` typed behaves normally). Offer to commit the target
   changes if they want.

Keep the human in the loop at the diff and at credentials — those are the two
places a mistake is costly.
