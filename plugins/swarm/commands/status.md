---
description: Show what each swarm agent is doing right now, with links to the issue, live checklist, and run log.
argument-hint: [issue#]
disable-model-invocation: true
---

# /swarm:status

Give a quick read on an in-flight (or finished) cycle: which agents are active and
on what, gates/escalations, tokens burned, and the links to dig in.

**Cycle:** `$ARGUMENTS` (the issue number; default: the most recent cycle).

1. If no argument, list cycles
   (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" cycles`) and use the latest.
2. Render the per-agent board:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" status --cycle <issue#>`.
   Show it as-is — it lists each **active agent and its current task** (with round
   and token counts), which roles are **idle**, open **gates/escalations**, total
   tokens, and last-activity time.
3. **Enrich the links** the script can't resolve on its own:
   - Resolve the working repo's `owner/repo` (from the git remote or GitHub MCP)
     and give the full **issue URL** for `#<issue#>`.
   - Find the live checklist: list the issue's comments, match the one containing
     `<!-- swarm:progress cycle=<issue#> -->`, and give its **permalink**.
   - Note the local **run log** path (shown by the board).
4. If the cycle is complete, offer the full report via the `debrief` skill. If it
   looks stuck (open gate/escalation, no recent activity), say so and point at
   the human gate, `/swarm:stop`, or — if a prior run was interrupted —
   `/swarm:start <issue#>` to resume it from the frontier.

Keep it to a tight, scannable summary — this is the "glance and know" command.
