---
name: release-android
description: Android release cartridge — build, test, and package an Android app for release via project scripts. Invoked when the active repo's cartridge is Android. Not for general use.
user-invocable: false
---

# release-android

The Android **cartridge**: stack-specific release steps, kept as a thin skill
that invokes the project's own scripts (release steps are better as scripts than
MCP servers). Orchestration stays stack-agnostic; this carries the Android
specifics.

## Preconditions

- Active repo declares the Android cartridge (its `CLAUDE.md` /
  `constitution.delta.md`).
- All required checks green; version/changelog prepared; no `risk:*` blockers
  open. Signing keys are **never** handled by an agent — release signing stays
  behind a human checkpoint.

## Steps (delegate to project scripts; do not reinvent)

1. `./gradlew test` (or the project's test task) — must pass.
2. `./gradlew lint` / static analysis — must pass.
3. Bump `versionCode` / `versionName` per the project's convention.
4. `./gradlew bundleRelease` (AAB) or `assembleRelease`.
5. Signing & upload to Play (internal/closed track) — **human checkpoint**;
   surface the artifact and stop for human approval. No standing prod credentials.

## Output

Build artifact path(s), test/lint results, the proposed version bump, and the
exact human action required to publish.

## Notes

If a step doesn't exist as a project script yet, file an issue to add it rather
than hard-coding it here — keep the cartridge thin.
