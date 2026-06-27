---
description: Gracefully stop a swarm cycle — release claimed work, mark it stopped, refresh the checklist.
argument-hint: [issue#]
disable-model-invocation: true
---

# /swarm:stop

Halt a running cycle cleanly. **Important:** the swarm runs *inside this Claude
Code session* — there is no background daemon to kill. To stop agents that are
actively executing **right now**, the user must press **Esc** to interrupt the
session; this command does the GitHub-side cleanup so nothing is left half-claimed.

**Cycle:** `$ARGUMENTS` (issue number; default: the most recent active cycle from
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" cycles`).

Steps:

1. **Confirm** with the user which cycle to stop and that they understand in-flight
   agents are halted by Esc (offer to proceed with cleanup regardless).
2. **Release locks.** For the cycle's sub-issues that are claimed
   (`in-progress` label / assignee), unassign them, remove `in-progress`, and add
   `needs-human` (or `blocked`) with a short comment that the cycle was stopped.
   This frees the work so it isn't seen as in-progress by a future run.
3. **Leave PRs in place** — don't close them; just list any open ones so the user
   can decide. Draft PRs can stay draft.
4. **Record it.** Log the stop and refresh the live checklist:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" log --cycle <issue#> \
       --event cycle_completed --detail "stopped by user"
   ```
   Then re-render the checklist
   (`swarm_log.py checklist --cycle <issue#>`) and update the
   `<!-- swarm:progress -->` comment so it shows ✅/⛔ stopped.
5. **Report** what was released (sub-issues, labels) and what was left as-is (open
   PRs, branches/worktrees), and how to resume (`/swarm:start <issue#>`).

Do not delete branches or worktrees, and do not revert merged work — stopping is
about releasing claims and recording state, not destroying progress.
