---
name: release-web
description: Web release cartridge — build, test, and deploy a web app for release via project scripts. Invoked when the active repo's cartridge is web. Not for general use.
user-invocable: false
---

# release-web

The web **cartridge**: stack-specific release steps as a thin skill over the
project's own scripts. Orchestration stays stack-agnostic; this carries the web
specifics.

## Preconditions

- Active repo declares the web cartridge.
- All required checks green; version/changelog prepared; no `risk:*` blockers
  open. Production deploy credentials stay behind a **human checkpoint** — never
  handed to an agent.

## Steps (delegate to project scripts; do not reinvent)

1. Install + build: `<pm> install` then `<pm> run build` — must succeed.
2. Test + lint + typecheck — must pass.
3. E2E smoke (Playwright MCP if configured) on a preview build; capture
   screenshots of key flows.
4. Version bump + changelog per the project's convention.
5. Deploy to **staging/preview**, verify, then **prod behind a human
   checkpoint** — surface the preview URL and stop for approval.

## Output

Build status, test/lint/typecheck results, E2E evidence (screenshots), preview
URL, proposed version bump, and the exact human action required to promote to
prod.

## Notes

Keep this thin — invoke project scripts; if a step is missing, file an issue to
add the script rather than embedding it here.
