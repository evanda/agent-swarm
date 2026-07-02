---
description: Check the central swarm repo for a newer release and bump this repo's pinned ref to adopt it.
argument-hint: [ref]
disable-model-invocation: true
---

# /swarm:update

Bump the marketplace pin in `.claude/settings.json` so this repo adopts the
latest central swarm plugin release — the *only* thing that needs to change to
adopt central improvements (§12 / `docs/decisions/0003-install-vs-runtime-boundary.md`
— reference, not vendor, so there's nothing else to sync).

**Target:** `$ARGUMENTS` (an explicit ref/tag to pin to, e.g. `v0.3.0`; default:
the central repo's latest release).

## Steps

1. **Find the central repo.** Read `.swarm/config.json`'s `central_repo`
   (`owner/repo`). If this file is absent, the swarm isn't installed here —
   stop and say so; this command has nothing to update.
2. **Find the current pin.** Read `.claude/settings.json` →
   `extraKnownMarketplaces.swarm.source.ref`. If that key is absent or its
   `source.repo` doesn't match `central_repo`, stop and say so rather than
   guessing which entry to touch.
3. **Find the target version.**
   - If `$ARGUMENTS` was given, use it as-is (no lookup).
   - Otherwise resolve the central repo's latest release tag:
     `gh release view --repo <central_repo> --json tagName -q .tagName`
     (fall back to `git ls-remote --tags https://github.com/<central_repo>.git`,
     sorted, if `gh` isn't available).
4. **Compare.** If the current pin already equals the target, report "already
   on `<ref>`" and stop — nothing to do.
5. **Show what's changing** before writing anything: fetch the target release's
   notes (`gh release view <tag> --repo <central_repo> --json body -q .body`)
   and summarize them for the human — this is the adoption boundary, so they
   should see what's landing before it takes effect on their next session.
6. **Write the new pin.** Edit only the matching `source.ref` value in
   `.claude/settings.json` — merge in place, never touch or reformat any other
   key (same discipline as the installer). Never edit files inside the plugin
   cache — this repo doesn't vendor the plugin, so there's nothing else to
   touch.
7. **Tell the human to reload.** The new ref only takes effect once the plugin
   cache re-fetches: `/reload-plugins` in this session, or a fresh session.
   Report the old ref → new ref and a one-line digest of what's in the bump.

## Must NOT

- Guess at a target repo/ref when `.swarm/config.json` or the marketplace entry
  is missing or ambiguous — stop and ask.
- Touch any file other than the one `ref` value in `.claude/settings.json`.
- Silently proceed without showing the human what's changing — this is how
  central improvements (including behavior changes) reach a consumer repo.
