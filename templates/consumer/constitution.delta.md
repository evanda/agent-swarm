# Constitution delta — <project name>

Repo-specific overrides and additions layered on the shared
`knowledge/constitution.md`. Keep this to genuine, stack-specific deltas; general
rules belong upstream in the shared constitution (see the `promote-learning`
litmus tests).

## Additional risk surfaces
<!-- e.g. "Any change under billing/ is risk:money even if it looks cosmetic." -->

## Stack-specific rules
<!-- e.g. "All DB migrations must be reversible and run behind a feature flag." -->

## Worktree provisioning
<!--
What a fresh `git worktree` needs before an agent can run the full verify suite
(tests + build + any asset pipeline) in it — filled in once, reused by every
Implementer. e.g.:
- Symlink `node_modules` and `public/tiles`/`public/fonts` from the main checkout
  instead of reinstalling per worktree.
- Pin the toolchain: node 22 (better-sqlite3 fails to build under node 26).
- Run `npm run build-atlas-webview` once per worktree before tests.
If this section is empty, the first Implementer to hit a missing-dependency wall
should record the working recipe here (via the Scribe) so later worktrees don't
repeat the discovery.
-->

## Cartridge
- Release cartridge: `release-web` <!-- or release-android -->

## Local notes
<!-- Instance-specific gotchas. e.g. "our webhook sends cents, not dollars." -->
