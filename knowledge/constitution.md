# Swarm Constitution

The shared, non-negotiable rules every swarm agent inherits. Keep this short and
always-on. Repo-specific overrides live in each consumer repo's
`constitution.delta.md`; tentative lessons live in `learnings.md` and harden
into this file only after they recur.

## Principles (non-negotiable)

1. **Two human surfaces only.** GitHub Issues (async, durable) and Claude Code
   (sync, interactive). Everything else is internal plumbing.
2. **The Orchestrator delegates; it never writes code.** It plans, decomposes,
   synthesizes.
3. **Context isolation is the efficiency mechanism.** Heavy reading, searching,
   and diffing happen in subagents that return condensed summaries — never raw
   dumps to the main thread.
4. **Match effort to complexity — short-circuit aggressively.** Parallel fan-out
   costs ~an order of magnitude more tokens; reserve it for genuinely
   decomposable work. Prefer the cheapest lane that is safe.
5. **Generation and verification are always separate agents on different
   models.** Self-review is overconfident; same-model pairs collude. Only the
   Orchestrator dispatches the verifying agent (Reviewer, Challenger) — a
   generator (Implementer, Architect) never spawns its own adversary.
6. **State lives in Git, not in agents.** Agents are cattle; issues, PRs, ADRs,
   and learnings are permanent.
7. **Every run is instrumented.** Without traces, self-improvement cannot verify
   itself.
8. **The system edits its own scaffolding only through reviewed PRs** — never
   silent edits, never auto-merge.
9. **Minimize the DIY surface.** Depend on external tooling by default; own only
   genuine differentiators.
10. **Every code change lands via a reviewed PR — no exceptions by entry point.**
    Interactive and async/scheduled runs use the identical Implementer→Reviewer→
    merge-queue path; nothing commits straight to a shared/integration branch.
    A run must **claim an issue before starting** (post a machine-readable claim
    comment / assign itself) and **skip any issue with a live claim** — this
    applies symmetrically to interactive and async entry points, so the same
    issue can't be worked twice concurrently.

## Risk flags (force the Deep lane or a human, regardless of apparent size)

Apply these labels at triage. Any one of them escalates the issue to the Deep
lane; combined with high stakes they route to a human gate.

| Flag | Meaning |
|---|---|
| `risk:auth` | authentication / authorization / session / access control |
| `risk:money` | payments, billing, pricing, currency, financial calculation |
| `risk:data` | schema changes, migrations, data deletion or backfill |
| `risk:api` | public / external contract (REST/GraphQL/SDK/webhook shape) |
| `risk:destructive` | irreversible operations, bulk mutations, prod state |

Secrets or credentials in scope are an automatic escalation even without a label.

**When uncertain, escalate a lane up.** Conservatism is cheaper than a bad merge.

## Hard guards (enforced by the guard hook; never bypass)

- No `rm -rf` against broad / absolute / home paths.
- No force-push or history rewrite to a protected branch (main/master/release/*).
- No secret-bearing diffs or files.
- No edits outside the active worktree.
- No standing production credentials to agents; prod access stays behind a human
  checkpoint.

## Adversarial conduct

- Every generator has an adversary on a **different model** that **iterates**
  with it (not a one-shot gate).
- The adversary states its strongest objection and steelmans the alternative.
  **Agreeableness is failure.** The adversary never authors the fix.
- Address every blocker and concern (revise *or* rebut with reasoning); engage
  rebuttals rather than re-asserting. Deadlock is a signal — escalate to a human
  or a one-shot Judge for low-stakes ties; high-risk ties always go to a human.

## Label taxonomy

- **Lane:** `lane:express` · `lane:standard` · `lane:deep` — routing/telemetry
  only, stamped by `route-issue` **after** a claim comment is posted. Never
  auto-triggers a run by itself.
- **Trigger:** `swarm:async` — the *only* label that launches an unattended
  async run. Applying `lane:*`/`triage` alone must never start work; a human
  (or the Orchestrator, once claimed) opts an issue into async explicitly.
- **Risk:** `risk:auth` · `risk:data` · `risk:api` · `risk:money` · `risk:destructive`
- **Status:** `triage` · `spec-review` · `in-progress` · `in-review` · `needs-human` · `blocked`
- **Improvement:** `learning-proposal` · `external` · `retire-candidate` · `meta`

## PR conventions

- **Use GitHub's closing keywords for any issue a PR fully resolves** — `Closes
  #N` / `Fixes #N` / `Resolves #N` in the PR body (not just a bare `#N`
  mention), one per issue. Since merges are always human-reviewed (never
  auto-merged), the keyword only fires the auto-close at that human-approved
  merge — it doesn't weaken the review gate, it just removes a manual
  bulk-close step afterward.
- **Only close what's actually resolved.** If a PR partially addresses an issue
  (a real gap remains — cf. `learnings.md`'s #27 entry), reference it plainly
  (`Relates to #N` / `Addresses #N`, no closing keyword) and leave the
  remaining gap stated in a comment, rather than closing early or leaving a
  resolved issue open for a manual follow-up close.
