# Consumer footprint (activate the swarm in an existing repo)

Copy these files into a project repo to make it **swarm-ready but dormant**
(§10A, §11). Nothing swarm-related fires until a human types `/swarm:*`.

```
my-app/
├── .claude/settings.json       # from settings.json here (extraKnownMarketplaces + project-scope install, pinned)
├── .swarm/config.json          # from swarm-config.json here
├── CLAUDE.md                   # from CLAUDE.md here (thin repo conventions)
├── constitution.delta.md       # from constitution.delta.md here (repo overrides)
├── specs/                      # Deep-lane artifacts (create empty)
└── docs/decisions/             # ADRs (create empty)
```

## Steps

1. Copy `settings.json` → `.claude/settings.json` (it registers the marketplace
   pinned to a tag and enables the plugin at **project** scope so it travels with
   the repo, including fresh cloud clones).
2. Copy `swarm-config.json` → `.swarm/config.json`.
3. Copy `CLAUDE.md` and `constitution.delta.md` to the repo root; edit for the
   project's stack and conventions. Pick the cartridge (`release-android` vs
   `release-web`).
4. In Claude Code: `/plugin install swarm@swarm` (choose **project** scope) then
   `/reload-plugins`.
5. Verify dormancy: run a plain `claude` session, type nothing `/swarm:*`, and
   confirm normal behavior (`/doctor` lists the commands as unused).

**Pinning is the adoption boundary** — bump the `ref` in `settings.json` when you
want the central repo's latest vetted changes.
