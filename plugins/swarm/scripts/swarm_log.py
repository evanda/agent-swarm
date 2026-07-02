#!/usr/bin/env python3
"""Swarm run log + the human-facing views rendered from it.

`.swarm/run-log.jsonl` is the per-run machine instrumentation (principle #7 —
"every run is instrumented"). Agents append structured events to it; this tool
renders two human views *from the same events* so they never drift:

  - checklist : the LIVE progress view for an in-flight cycle (mirrored into a
                GitHub issue comment by the Scribe, refreshed at each boundary)
  - debrief   : the comprehensive end-of-cycle report (posted to the issue and,
                if configured, committed to docs/debriefs/<cycle>.md)

Usage:
  swarm_log.py log --cycle 42 --event agent_dispatched --agent implementer \\
      --detail "task: add /health/ready endpoint" [--lane deep] [--task t3] \\
      [--round 1] [--tokens 8200] [--status in_progress] [--data '{"pr":12}']
  swarm_log.py checklist --cycle 42        # render the live checklist (markdown)
  swarm_log.py debrief   --cycle 42        # render the full debrief (markdown)
  swarm_log.py cycles                      # list cycles present in the log
  swarm_log.py frontier  --cycle 42 [--ground-truth '{...}'] [--json]
      # deterministic per-task next-stage (done/resume/dispatch/crashed) from
      # the log, reconciled against ground truth if given — resume-cycle Step 3

The log file defaults to ./.swarm/run-log.jsonl (repo root); override with --file.
"""
import argparse
import datetime
import json
import os
import sys

DEFAULT_LOG = os.path.join(".swarm", "run-log.jsonl")

# The closed event vocabulary. Keep this in lockstep with the run-log skill.
EVENTS = {
    "cycle_started",     # a swarm cycle begins (one issue)
    "lane_routed",       # route-issue picked a lane (+ risk flags)
    "agent_dispatched",  # a subagent was spawned for a unit of work
    "agent_returned",    # that subagent returned its condensed result
    "dialectic_round",   # one generator<->adversary round
    "decision",          # a recorded decision (ADR-worthy or notable)
    "gate",              # a human gate reached (e.g. spec-review)
    "escalation",        # deadlock / risk tie / needs-human
    "pr_opened",         # a PR was opened
    "pr_merged",         # a PR landed via the merge queue
    "note",              # freeform annotation
    "cycle_completed",   # the cycle ended (success or stopped)
}

ICON = {"done": "x", "in_progress": " ", "blocked": " ", "pending": " ", "crashed": "!"}
MARK = {"in_progress": " ⏳", "blocked": " ⛔", "pending": "", "done": "", "crashed": " 💥"}

# The role spine (§2) — used to show which agents are idle in the status board.
ROLES = ["orchestrator", "explorer", "architect", "challenger", "implementer",
         "reviewer", "integrator", "scribe", "improver", "scout"]


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def read_events(path, cycle=None):
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                sys.stderr.write(f"WARN: {path}:{i} is not valid JSON; skipped\n")
                continue
            if cycle is None or str(ev.get("cycle")) == str(cycle):
                out.append(ev)
    return out


# --- log --------------------------------------------------------------------
def cmd_log(args):
    if args.event not in EVENTS:
        sys.exit(f"ERROR: unknown event {args.event!r}. One of: {', '.join(sorted(EVENTS))}")
    ev = {"ts": now_iso(), "cycle": str(args.cycle), "event": args.event}
    for k in ("agent", "lane", "detail", "task", "status"):
        v = getattr(args, k)
        if v is not None:
            ev[k] = v
    if args.round is not None:
        ev["round"] = args.round
    if args.tokens is not None:
        ev["tokens"] = args.tokens
    if args.data:
        try:
            ev["data"] = json.loads(args.data)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: --data is not valid JSON: {e}")
    os.makedirs(os.path.dirname(args.file) or ".", exist_ok=True)
    with open(args.file, "a") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    print(f"logged: {ev['event']} (cycle {ev['cycle']})")


# --- shared rendering helpers ----------------------------------------------
def pair_work_items(events):
    """Pair agent_dispatched with its agent_returned by (agent, task|detail)."""
    items = []  # ordered
    index = {}
    for ev in events:
        if ev["event"] == "agent_dispatched":
            key = (ev.get("agent"), ev.get("task") or ev.get("detail"))
            it = {"agent": ev.get("agent"), "label": ev.get("detail") or ev.get("task") or "(work)",
                  "status": ev.get("status", "in_progress"), "rounds": 0,
                  "tokens": ev.get("tokens", 0)}
            index[key] = it
            items.append(it)
        elif ev["event"] == "agent_returned":
            key = (ev.get("agent"), ev.get("task") or ev.get("detail"))
            it = index.get(key)
            if it:
                it["status"] = ev.get("status", "done")
                it["tokens"] += ev.get("tokens", 0) or 0
            else:
                items.append({"agent": ev.get("agent"), "label": ev.get("detail") or "(returned)",
                              "status": ev.get("status", "done"), "rounds": 0,
                              "tokens": ev.get("tokens", 0)})
        elif ev["event"] == "dialectic_round":
            key = (ev.get("agent"), ev.get("task") or ev.get("detail"))
            it = index.get(key)
            if it:
                it["rounds"] = max(it["rounds"], ev.get("round", it["rounds"]))
    return items


def total_tokens(events):
    return sum(int(ev.get("tokens", 0) or 0) for ev in events)


# --- frontier (deterministic resume reconcile) -------------------------------
ROLE_STAGE = {"implementer": "implement", "reviewer": "review", "integrator": "merge"}


def compute_frontier(events, ground_truth=None):
    """Compute each task's next-incomplete-stage from run-log events, then
    reconcile against ground truth (reality wins over the log, per the
    resume-cycle skill). Deterministic — no model judgment.

    `ground_truth`, if given, is a dict:
      {"open_prs": [...], "merged_prs": [...],
       "sub_issues": {task_id: "open|closed[, label: ..., assignee: ...]"},
       "worktrees": {task_id: "present, ..."}}

    Returns (frontier, notes):
      frontier: {task_id: "done" | "resume" | "dispatch" | "crashed"}
        - done     — merged (or ground truth shows closed); nothing to do.
        - resume   — implement and/or review started but not merged; continue
                     from here, don't restart from scratch.
        - dispatch — no work logged yet for this task.
        - crashed  — an `agent_returned --status crashed` was recorded; must be
                     re-verified against spec/critique before advancing (never
                     silently treated as done or auto-resumed).
      notes: human-readable corrections made from reconciling against reality.
    """
    tasks = {}

    def rec(task_id):
        return tasks.setdefault(task_id, {"implement": "pending", "review": "pending",
                                           "merge": "pending", "crashed": False})

    for ev in events:
        task_id = ev.get("task")
        if not task_id:
            continue
        r = rec(task_id)
        stage = ROLE_STAGE.get(ev.get("agent"), "implement")
        if ev["event"] == "agent_dispatched" and r[stage] == "pending":
            r[stage] = "in_progress"
        elif ev["event"] == "agent_returned":
            status = ev.get("status", "done")
            r[stage] = status
            if status == "crashed":
                r["crashed"] = True
        elif ev["event"] == "pr_merged":
            r["merge"] = "done"

    notes = []
    if ground_truth:
        sub_issues = ground_truth.get("sub_issues", {})
        worktrees = ground_truth.get("worktrees", {})
        # Ground truth can name a sub-issue the log never mentions at all (never
        # dispatched, or dispatched on a machine whose log we don't have).
        for task_id in sub_issues:
            if task_id not in tasks:
                rec(task_id)
        for task_id, r in tasks.items():
            si = sub_issues.get(task_id, "")
            if "closed" in si and r["merge"] != "done":
                r["implement"] = r["review"] = r["merge"] = "done"
                notes.append(f"{task_id}: log lagged reality — ground truth shows the "
                             f"sub-issue closed/merged; corrected to done")
            elif task_id in worktrees and r["implement"] == "pending":
                r["implement"] = "in_progress"
                notes.append(f"{task_id}: log shows no dispatch but a worktree with "
                             f"on-disk changes exists; treated as in-progress, not fresh")

    frontier = {}
    for task_id, r in tasks.items():
        if r["crashed"]:
            frontier[task_id] = "crashed"
        elif r["merge"] == "done":
            frontier[task_id] = "done"
        elif r["implement"] == "pending" and r["review"] == "pending":
            frontier[task_id] = "dispatch"
        else:
            frontier[task_id] = "resume"
    return frontier, notes


def cmd_frontier(args):
    events = read_events(args.file, args.cycle)
    if not events:
        print(f"No events for cycle {args.cycle}.")
        return
    ground_truth = None
    if args.ground_truth:
        try:
            ground_truth = json.loads(args.ground_truth)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: --ground-truth is not valid JSON: {e}")
    frontier, notes = compute_frontier(events, ground_truth)
    if args.json:
        print(json.dumps({"frontier": frontier, "notes": notes}, indent=2))
        return
    if not frontier:
        print("No task-scoped events found (events need --task to be tracked here).")
        return
    for task_id, action in frontier.items():
        print(f"{task_id}: {action}")
    for n in notes:
        print(f"note: {n}")


def first(events, name):
    for ev in events:
        if ev["event"] == name:
            return ev
    return None


def last(events, name):
    found = None
    for ev in events:
        if ev["event"] == name:
            found = ev
    return found


# --- status (compact per-agent board) ---------------------------------------
def cmd_status(args):
    events = read_events(args.file, args.cycle)
    if not events:
        print(f"No events for cycle {args.cycle} in {args.file}.")
        return
    routed = first(events, "lane_routed")
    done = first(events, "cycle_completed")
    items = pair_work_items(events)
    active = [it for it in items if it["status"] in ("in_progress", "blocked")]
    crashed = [it for it in items if it["status"] == "crashed"]
    active_agents = {it["agent"] for it in active}
    open_gates = [e for e in events if e["event"] == "gate"]
    open_escs = [e for e in events if e["event"] == "escalation"]
    last_ev = events[-1]

    lane = (routed or {}).get("lane", "?")
    risk = (routed or {}).get("detail", "")
    head = f"🐝 Swarm cycle {args.cycle} — {lane}" + (f" ({risk})" if risk else "")
    state = ("✅ completed" if done else
             "💥 crashed" if crashed else
             "⛔ blocked" if any(i['status']=='blocked' for i in active) else "running")
    print(head)
    print(f"State: {state} · last activity {last_ev['ts']} · ~{total_tokens(events)/1000:.1f}k tokens")
    print("")
    print("Agents:")
    if active:
        for it in active:
            rd = f" (round {it['rounds']})" if it["rounds"] else ""
            tok = f" · ~{it['tokens']/1000:.1f}k tok" if it["tokens"] else ""
            flag = "⛔" if it["status"] == "blocked" else "⏳"
            print(f"  {flag} {it['agent']:<12} {it['label']}{rd}{tok}")
    else:
        print("  (no agent currently active)")
    if crashed:
        print("")
        for it in crashed:
            print(f"  💥 {it['agent']:<12} {it['label']} — crashed, needs re-verification before resume")
    idle = [r for r in ROLES if r not in active_agents]
    if idle and not done:
        print(f"  · idle: {', '.join(idle)}")
    if open_gates or open_escs:
        print("")
        for g in open_gates:
            print(f"  ⚠️ gate: {g.get('detail','(human gate)')}")
        for e in open_escs:
            print(f"  ⛔ escalation: {e.get('detail','(needs human)')}")
    print("")
    print("Links:")
    print(f"  issue   : #{args.cycle}")
    print(f"  run log : {args.file}")
    print(f"  checklist: the <!-- swarm:progress --> comment on issue #{args.cycle}")
    print("\n(For the full live checklist: `swarm_log.py checklist --cycle "
          f"{args.cycle}`; for the report: `swarm_log.py debrief --cycle {args.cycle}`.)")


# --- checklist --------------------------------------------------------------
def cmd_checklist(args):
    events = read_events(args.file, args.cycle)
    if not events:
        print(f"No events for cycle {args.cycle}.")
        return
    routed = first(events, "lane_routed")
    started = first(events, "cycle_started")
    lane = (routed or {}).get("lane", "?")
    risk = (routed or {}).get("detail", "")
    lines = [f"<!-- swarm:progress cycle={args.cycle} -->",
             f"### 🐝 Swarm progress — cycle {args.cycle}",
             f"**Lane:** {lane}" + (f" · **Risk/notes:** {risk}" if risk else "") +
             (f" · started {started['ts']}" if started else ""), ""]
    if routed:
        lines.append(f"- [x] routed → {lane}" + (f" ({risk})" if risk else ""))
    for it in pair_work_items(events):
        box = ICON.get(it["status"], " ")
        rd = f" (round {it['rounds']})" if it["rounds"] else ""
        tok = f" · ~{it['tokens']/1000:.1f}k tok" if it["tokens"] else ""
        lines.append(f"- [{box}]{MARK.get(it['status'],'')} **{it['agent']}**: {it['label']}{rd}{tok}")
    gates = [e for e in events if e["event"] == "gate"]
    escs = [e for e in events if e["event"] == "escalation"]
    for g in gates:
        lines.append(f"- [ ] ⚠️ gate: {g.get('detail','(human gate)')}")
    for e in escs:
        lines.append(f"- [ ] ⛔ escalation: {e.get('detail','(needs human)')}")
    prs = [e for e in events if e["event"] in ("pr_opened", "pr_merged")]
    if prs:
        lines.append("")
        for p in prs:
            verb = "merged" if p["event"] == "pr_merged" else "opened"
            lines.append(f"- PR {verb}: {p.get('detail','')}")
    done = first(events, "cycle_completed")
    status = "✅ completed" if done else "in progress"
    lines += ["", f"_Status: {status} · {len(events)} events · ~{total_tokens(events)/1000:.1f}k tokens · "
              f"updated {now_iso()}_", "<!-- /swarm:progress -->"]
    print("\n".join(lines))


# --- debrief ----------------------------------------------------------------
def cmd_debrief(args):
    events = read_events(args.file, args.cycle)
    if not events:
        print(f"No events for cycle {args.cycle}.")
        return
    routed = first(events, "lane_routed")
    started = first(events, "cycle_started")
    done = first(events, "cycle_completed")
    items = pair_work_items(events)
    decisions = [e for e in events if e["event"] == "decision"]
    rounds = [e for e in events if e["event"] == "dialectic_round"]
    gates = [e for e in events if e["event"] in ("gate", "escalation")]
    prs = [e for e in events if e["event"] in ("pr_opened", "pr_merged")]

    L = []
    L.append(f"# Swarm debrief — cycle {args.cycle}")
    L.append("")
    L.append(f"- **Lane:** {(routed or {}).get('lane','?')}")
    if routed and routed.get("detail"):
        L.append(f"- **Risk / routing rationale:** {routed['detail']}")
    if started:
        L.append(f"- **Started:** {started['ts']}")
    if done:
        L.append(f"- **Completed:** {done['ts']}" + (f" — {done.get('detail','')}" if done.get("detail") else ""))
    L.append(f"- **Subagents dispatched:** {sum(1 for e in events if e['event']=='agent_dispatched')}")
    L.append(f"- **Dialectic rounds:** {len(rounds)}")
    L.append(f"- **Estimated tokens:** ~{total_tokens(events)/1000:.1f}k")
    L.append("")

    L.append("## What the swarm did")
    if items:
        for it in items:
            rd = f", {it['rounds']} dialectic round(s)" if it["rounds"] else ""
            tok = f" (~{it['tokens']/1000:.1f}k tok)" if it["tokens"] else ""
            L.append(f"- **{it['agent']}** — {it['label']} → _{it['status']}_{rd}{tok}")
    else:
        L.append("- (no agent activity recorded)")
    L.append("")

    L.append("## Decisions & rejected alternatives")
    if decisions:
        for d in decisions:
            L.append(f"- {d.get('detail','(decision)')}" +
                     (f"  ({d['data'].get('adr')})" if isinstance(d.get("data"), dict) and d["data"].get("adr") else ""))
    else:
        L.append("- (none recorded — link ADRs from docs/decisions/ here)")
    L.append("")

    L.append("## Human gates & escalations")
    if gates:
        for g in gates:
            tag = "gate" if g["event"] == "gate" else "escalation"
            L.append(f"- **{tag}:** {g.get('detail','')} ({g['ts']})")
    else:
        L.append("- (none)")
    L.append("")

    L.append("## Changes (PRs)")
    if prs:
        for p in prs:
            verb = "merged" if p["event"] == "pr_merged" else "opened"
            L.append(f"- PR {verb}: {p.get('detail','')}")
    else:
        L.append("- (none)")
    L.append("")

    L.append("## Adversarial health")
    L.append(f"- Dialectic rounds: {len(rounds)} · escalations: "
             f"{sum(1 for e in events if e['event']=='escalation')}")
    L.append("- Rubber-stamp / false-block notes: _(Scribe: fill from review outcomes)_")
    L.append("")

    L.append("## For the Improver")
    L.append("- Candidate learnings (failure classes, routing misses, cost surprises): "
             "_(Scribe: distill from above and file as learning-proposals)_")
    L.append("")

    L.append("## Timeline")
    for e in events:
        bits = [e["ts"], e["event"]]
        if e.get("agent"):
            bits.append(e["agent"])
        if e.get("detail"):
            bits.append("— " + e["detail"])
        L.append(f"- `{bits[0]}` **{bits[1]}** " + " ".join(bits[2:]))
    L.append("")
    print("\n".join(L))


def cmd_cycles(args):
    events = read_events(args.file)
    seen = {}
    for e in events:
        c = str(e.get("cycle"))
        seen.setdefault(c, 0)
        seen[c] += 1
    if not seen:
        print("No cycles logged.")
        return
    for c, n in seen.items():
        print(f"cycle {c}: {n} events")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=DEFAULT_LOG, help=f"run log path (default {DEFAULT_LOG})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("log", help="append an event")
    lg.add_argument("--cycle", required=True)
    lg.add_argument("--event", required=True)
    lg.add_argument("--agent")
    lg.add_argument("--lane")
    lg.add_argument("--detail")
    lg.add_argument("--task")
    lg.add_argument("--status", choices=["pending", "in_progress", "done", "blocked", "crashed"])
    lg.add_argument("--round", type=int)
    lg.add_argument("--tokens", type=int)
    lg.add_argument("--data", help="extra JSON object")
    lg.set_defaults(func=cmd_log)

    st = sub.add_parser("status", help="compact per-agent board (who's doing what now)")
    st.add_argument("--cycle", required=True)
    st.set_defaults(func=cmd_status)

    cl = sub.add_parser("checklist", help="render the live progress checklist")
    cl.add_argument("--cycle", required=True)
    cl.set_defaults(func=cmd_checklist)

    db = sub.add_parser("debrief", help="render the end-of-cycle debrief")
    db.add_argument("--cycle", required=True)
    db.set_defaults(func=cmd_debrief)

    cy = sub.add_parser("cycles", help="list cycles present in the log")
    cy.set_defaults(func=cmd_cycles)

    fr = sub.add_parser("frontier", help="deterministic per-task next-stage (resume-cycle Step 3)")
    fr.add_argument("--cycle", required=True)
    fr.add_argument("--ground-truth", help="JSON: open_prs/merged_prs/sub_issues/worktrees, reconciled over the log")
    fr.add_argument("--json", action="store_true", help="machine-readable output")
    fr.set_defaults(func=cmd_frontier)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
