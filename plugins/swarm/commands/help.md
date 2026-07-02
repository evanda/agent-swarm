---
description: Show how to use the swarm — all commands, how to check progress, how to stop a run, and where everything lives.
argument-hint:
disable-model-invocation: true
---

# /swarm:help

Present the reference below to the user, clearly and concisely. If a cycle is
currently running (check
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" cycles`), add a one-line
"currently running: cycle #N — see /swarm:status" note at the top. Adapt wording,
but keep all the facts.

---

## 🐝 Swarm — quick reference

The swarm is a team of specialized agents that take work from GitHub Issues,
route it by risk into a lane, and deliver verified PRs. It is **dormant** until
you summon it — a plain session with no `/swarm:` typed behaves 100% normally.

### Run work
- **`/swarm:start <issue# | description>`** — the main entry. Triages, routes
  (Express / Standard / Deep), and runs the lane: delegate → review → merge.
- **`/swarm:express <description>`** — force the cheap Express lane for a known
  trivial, reversible, well-tested fix (sanity-checked; escalates if risky).
- **Async (no session):** file/assign a GitHub Issue and add the `swarm:async`
  label; the scheduled job picks it up. `lane:*`/`triage` alone never triggers a
  run — they're routing/telemetry, stamped after a claim. The async picker
  claims before starting (skips issues with a live claim) and always lands its
  result through the normal Implementer→Reviewer→merge-queue path, never a
  direct commit.

### Watch it
- **`/swarm:status [issue#]`** — what each agent is doing right now, idle roles,
  gates, tokens burned, and links to the issue / live checklist / run log.
- **Ambient live view (no polling):** run
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/swarm_log.py" watch --cycle <issue#>`
  in a side terminal — a self-refreshing swimlane (one row per role) instead of
  re-running `/swarm:status` by hand.
- **Live checklist:** a single auto-updating comment on the issue (the
  `<!-- swarm:progress -->` comment), refreshed at every step.
- **Run log:** `.swarm/run-log.jsonl` in this repo (raw event stream).

### Stop it
- **`/swarm:stop [issue#]`** — gracefully halt a cycle: release claimed
  sub-issues, mark the cycle stopped, and refresh the checklist.
- **Hard interrupt:** the swarm runs *inside this Claude Code session* — there is
  no separate daemon. Press **Esc** to immediately interrupt agents mid-run, then
  run `/swarm:stop` to clean up GitHub-side state (claims/labels).

### Review & learn
- **`/swarm:retro [scope]`** — retrospective on recent work → learning-proposals.
- **Debrief:** at cycle end the swarm posts a comprehensive report (what each
  agent did, decisions, PRs, token cost, timeline) to the issue (and optionally
  `docs/debriefs/<issue#>.md`).

### Where things live
- `specs/<issue#>/` — Deep-lane spec/plan/tasks · `docs/decisions/` — ADRs ·
  `docs/debriefs/` — per-cycle reports (if committed) · `.swarm/config.json` —
  settings (`central_repo`, `cartridge`, `debrief`) · `constitution.delta.md` —
  this repo's rule overrides.

### Safety
- A guard hook blocks `rm -rf` on broad paths, force-push to protected branches,
  secret-bearing diffs, and edits outside the active worktree — even in plain
  sessions.
- Risk-flagged work (`risk:auth|money|data|api|destructive`) is forced to the
  Deep lane with a human gate. No standing prod credentials reach agents.

_Type `/swarm:status` to see the current run, or `/swarm:start <issue#>` to begin._
