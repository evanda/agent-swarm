# Scout sources

Curated external sources the Scout scans on each outward-loop run (§8). Keep
this list tight and high-signal; prune sources that never yield adoptable
findings. The Scout also runs targeted searches for each `revisit_if` trigger in
`dependencies.md`.

## Anthropic / Claude Code
- Anthropic news & changelog — https://www.anthropic.com/news
- Claude Code docs & release notes — https://docs.claude.com/en/docs/claude-code
- `anthropics/claude-code` (plugins: feature-dev, pr-review-toolkit) — https://github.com/anthropics/claude-code
- `claude-plugins-official` (skill-creator and friends)
- `anthropics/skills` — https://github.com/anthropics/skills

## Spec / workflow tooling
- `github/spec-kit` releases — https://github.com/github/spec-kit/releases

## Practitioners & best practice
- Key practitioners writing on agentic dev workflows, eval design, and
  multi-agent orchestration (curate 3–5 high-signal feeds; revisit quarterly).

## Scan discipline
- **Default verdict is Watch** for anything immature.
- Require a maturity bar before Adopt/Adapt.
- Weight reversibility and portability heavily; avoid lock-in.
- File Adopt/Adapt findings (or tripped triggers → Retire) as `external`-labeled
  `learning-proposal` issues in this repo.
- **Re-pin cadence (anti-thrash):** for an already-`adapt`/`adopt` dependency with
  no `revisit_if` signal and no wrapper change required, batch routine patch-level
  re-pins to **weekly** rather than filing a proposal on every upstream release —
  a fast-moving dependency (e.g. `spec-kit`) can ship daily and each patch-only
  re-pin is otherwise ledger churn with no decision content. Re-pin immediately,
  outside the cadence, whenever a scan finds a `revisit_if`-relevant change or a
  minor/major version bump.
