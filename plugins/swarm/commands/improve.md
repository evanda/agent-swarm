---
description: Run the inward self-improvement loop (Improver) in this session — process learning-proposals, run evals, open one reviewed PR. Uses your subscription, no API key.
argument-hint:
disable-model-invocation: true
---

# /swarm:improve

Run the **Improver** loop (see `plugins/swarm/agents/improver.md`) right here, in
this Claude Code session — so it draws on your subscription, not the Anthropic API.
Run it manually, or have a scheduled Claude routine invoke it (see the README's
"Running the loops on your subscription").

Do exactly what the Improver agent specifies:

1. Read open `learning-proposal` issues and `.swarm/run-log.jsonl`; run sampled
   `interrogate` weighted to bad outcomes / low-confidence / risk.
2. Apply the smallest correct edits via `promote-learning` (constitution / skill /
   CLAUDE.md / learnings), grouping related changes.
3. **Verify — run the evals:** `python3 knowledge/evals/run.py --llm`. Confirm **no
   regression** before opening anything.
4. Open **one** PR on a new branch, labeled `meta`, linking the proposals it
   resolves, and bump `plugins/swarm/.claude-plugin/plugin.json` `version`.
   **Do not merge it** — the human merges.
5. Report the metrics (rubber-stamp / false-block / deadlock rates) in the PR body.

Stop and ask if a proposed change is stack-specific (would pollute shared scope)
or if an edit regresses an eval.
