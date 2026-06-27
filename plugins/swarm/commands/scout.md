---
description: Run the outward self-improvement loop (Scout) in this session — scan SOTA tooling, score findings, file proposals. Uses your subscription, no API key.
argument-hint:
disable-model-invocation: true
---

# /swarm:scout

Run the **Scout** loop (see `plugins/swarm/agents/scout.md`) right here, in this
Claude Code session — so it draws on your subscription, not the Anthropic API.
Run it manually, or have a scheduled Claude routine invoke it (see the README's
"Running the loops on your subscription").

Do exactly what the Scout agent specifies:

1. Scan `knowledge/scout-sources.md`, then run targeted searches for each
   `revisit_if` trigger in `knowledge/dependencies.md`.
2. Score each finding with the `scout-scan` scorecard (Fit / Maturity /
   Maintenance-delta / Portability / Migration-cost / Risk → Adopt / Adapt /
   Watch / Pass). Default to **Watch** for immature things.
3. Validate any Adopt/Adapt candidate with `eval-dependency` before recommending it.
4. File Adopt/Adapt findings (or a tripped trigger → propose **Retire**) as
   `external`-labeled `learning-proposal` issues, each with its scorecard and a
   proposed `dependencies.md` row. **Adopt nothing without a reviewed PR.**
