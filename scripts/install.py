#!/usr/bin/env python3
"""Install the swarm into a target project repo (the consumer footprint, §10A/§11).

Run this from the agent-swarm (central) repo, pointing at a sibling clone of the
project you want to activate. It does the *safe, deterministic* part of the
bootstrap:

  - merges the marketplace + plugin-enable into an existing .claude/settings.json
    (never clobbers other keys; backs up first)
  - injects/refreshes a delimited "swarm" block in an existing CLAUDE.md
    (idempotent; leaves the rest of the file untouched)
  - creates .swarm/config.json and constitution.delta.md only if absent
  - creates the specs/ and docs/decisions/ directories

The fuzzy parts (reconciling CLAUDE.md prose, choosing the cartridge, wiring
credentials) are left to the human / the /install command that wraps this.

Usage:
  python3 scripts/install.py <target-repo-path> [options]

Options:
  --cartridge {release-web,release-android}   default: release-web
  --ref <git-ref>        marketplace pin (default: read from plugin.json or 'main')
  --central <owner/repo> central repo slug (default: from .swarm/config.json)
  --dry-run              print planned actions; write nothing
  --force               overwrite create-if-absent files (config, delta) too

Idempotent: re-running updates the marketplace ref and the CLAUDE.md block in
place rather than duplicating them.
"""
import argparse
import datetime
import json
import os
import sys

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BEGIN = "<!-- BEGIN swarm (managed by agent-swarm installer; edits between markers may be overwritten) -->"
END = "<!-- END swarm -->"

CLAUDE_BLOCK = """## Swarm

The dev swarm is **available but dormant** in this repo. Summon it explicitly:

- `/swarm:start <issue#-or-description>` — triage, route, and run the lane.
- `/swarm:express <description>` — force the Express lane for a known-trivial fix.
- `/swarm:retro` — retrospective on recent work.

Repo-specific overrides live in `constitution.delta.md`. Nothing swarm-related
fires until you type a `/swarm:*` command — *no `/swarm:` typed = no swarm.*"""

DELTA_TEMPLATE = """# Constitution delta — {name}

Repo-specific overrides and additions layered on the shared
`knowledge/constitution.md`. Keep this to genuine, stack-specific deltas; general
rules belong upstream (see the `promote-learning` litmus tests).

## Additional risk surfaces
<!-- e.g. "Any change under billing/ is risk:money even if it looks cosmetic." -->

## Stack-specific rules
<!-- e.g. "All DB migrations must be reversible and run behind a feature flag." -->

## Cartridge
- Release cartridge: `{cartridge}`

## Local notes
<!-- Instance-specific gotchas. e.g. "our webhook sends cents, not dollars." -->
"""

actions = []   # (verb, path, detail)
dry = False


def record(verb, path, detail=""):
    actions.append((verb, path, detail))


def backup(path):
    if dry or not os.path.exists(path):
        return None
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = f"{path}.{stamp}.bak"
    with open(path) as f:
        data = f.read()
    with open(bak, "w") as f:
        f.write(data)
    return bak


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {path} exists but is not valid JSON ({e}); fix it before installing.")


def write_json(path, obj):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def detect_default_ref():
    plugin = read_json(os.path.join(SRC_ROOT, "plugins/swarm/.claude-plugin/plugin.json"))
    if plugin and plugin.get("version"):
        return "v" + plugin["version"]
    return "main"


def detect_central():
    cfg = read_json(os.path.join(SRC_ROOT, ".swarm/config.json"))
    if cfg and cfg.get("central_repo"):
        return cfg["central_repo"]
    return "evanda/agent-swarm"


# --- operations -------------------------------------------------------------
def merge_settings(target, central, ref):
    path = os.path.join(target, ".claude/settings.json")
    existing = read_json(path) or {}
    before = json.dumps(existing, sort_keys=True)

    mkts = existing.setdefault("extraKnownMarketplaces", {})
    desired_src = {"source": "github", "repo": central, "ref": ref}
    prev = mkts.get("swarm", {}).get("source") if isinstance(mkts.get("swarm"), dict) else None
    mkts["swarm"] = {"source": desired_src}

    enabled = existing.setdefault("enabledPlugins", [])
    if "swarm@swarm" not in enabled:
        enabled.append("swarm@swarm")

    after = json.dumps(existing, sort_keys=True)
    if before == after:
        record("unchanged", path, "marketplace + plugin already registered")
        return
    bak = backup(path)
    write_json(path, existing)
    detail = "merged extraKnownMarketplaces.swarm + enabledPlugins"
    if prev and prev != desired_src:
        detail += f" (updated pin {prev.get('ref')} -> {ref})"
    if bak:
        detail += f"; backed up -> {os.path.basename(bak)}"
    record("merged", path, detail)


def merge_claude_md(target):
    path = os.path.join(target, "CLAUDE.md")
    block = f"{BEGIN}\n{CLAUDE_BLOCK}\n{END}\n"
    if not os.path.exists(path):
        if not dry:
            with open(path, "w") as f:
                f.write(f"# {os.path.basename(os.path.abspath(target))}\n\n{block}")
        record("created", path, "new CLAUDE.md with swarm block")
        return
    with open(path) as f:
        text = f.read()
    if BEGIN in text and END in text:
        pre = text[: text.index(BEGIN)]
        post = text[text.index(END) + len(END):]
        new = pre + block.rstrip("\n") + post
        if new == text:
            record("unchanged", path, "swarm block already current")
            return
        backup(path)
        if not dry:
            with open(path, "w") as f:
                f.write(new)
        record("updated", path, "refreshed swarm block in place")
    else:
        backup(path)
        if not dry:
            sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
            with open(path, "a") as f:
                f.write(f"{sep}{block}")
        record("appended", path, "added swarm block (existing content untouched)")


def create_if_absent_config(target, central, cartridge, force):
    path = os.path.join(target, ".swarm/config.json")
    existing = read_json(path)
    if existing is not None and not force:
        # fill in any missing keys without disturbing the rest
        changed = False
        if "central_repo" not in existing:
            existing["central_repo"] = central; changed = True
        if "cartridge" not in existing:
            existing["cartridge"] = cartridge; changed = True
        if changed:
            backup(path); write_json(path, existing)
            record("merged", path, "added missing keys")
        else:
            record("unchanged", path, "already configured")
        return
    write_json(path, {"central_repo": central, "cartridge": cartridge})
    record("created" if existing is None else "overwrote", path, f"central={central}, cartridge={cartridge}")


def create_if_absent_delta(target, cartridge, force):
    path = os.path.join(target, "constitution.delta.md")
    if os.path.exists(path) and not force:
        record("unchanged", path, "kept existing delta")
        return
    name = os.path.basename(os.path.abspath(target))
    verb = "overwrote" if os.path.exists(path) else "created"
    if not dry:
        with open(path, "w") as f:
            f.write(DELTA_TEMPLATE.format(name=name, cartridge=cartridge))
    record(verb, path, "from template")


def ensure_dirs(target):
    for d in ("specs", "docs/decisions"):
        p = os.path.join(target, d)
        keep = os.path.join(p, ".gitkeep")
        if os.path.exists(p):
            record("unchanged", p + "/", "exists")
            continue
        if not dry:
            os.makedirs(p, exist_ok=True)
            open(keep, "w").close()
        record("created", p + "/", "with .gitkeep")


def main():
    global dry
    ap = argparse.ArgumentParser(description="Install the swarm into a target project repo.")
    ap.add_argument("target", help="path to the target project repo")
    ap.add_argument("--cartridge", choices=["release-web", "release-android"], default="release-web")
    ap.add_argument("--ref", default=None, help="marketplace pin (default: plugin version tag)")
    ap.add_argument("--central", default=None, help="central repo slug owner/repo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite create-if-absent files too")
    args = ap.parse_args()

    dry = args.dry_run
    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        sys.exit(f"ERROR: target path does not exist: {target}")
    if os.path.abspath(target) == SRC_ROOT:
        sys.exit("ERROR: target is the agent-swarm repo itself; point at the project to activate.")
    if not os.path.isdir(os.path.join(target, ".git")):
        print(f"WARNING: {target} is not a git repo (no .git). Continuing anyway.")

    central = args.central or detect_central()
    ref = args.ref or detect_default_ref()

    print(f"Installing swarm into: {target}")
    print(f"  central_repo : {central}")
    print(f"  marketplace ref: {ref}")
    print(f"  cartridge    : {args.cartridge}")
    print(f"  mode         : {'DRY RUN (no writes)' if dry else 'apply'}\n")

    merge_settings(target, central, ref)
    merge_claude_md(target)
    create_if_absent_config(target, central, args.cartridge, args.force)
    create_if_absent_delta(target, args.cartridge, args.force)
    ensure_dirs(target)

    print("Plan:" if dry else "Done:")
    width = max((len(v) for v, _, _ in actions), default=0)
    for verb, path, detail in actions:
        rel = os.path.relpath(path, target)
        print(f"  {verb.ljust(width)}  {rel}" + (f"  — {detail}" if detail else ""))

    print("\nNext steps (human):")
    print("  1. Review the diff in the target repo (especially CLAUDE.md / settings.json).")
    print("  2. In Claude Code from the target repo: /plugin install swarm@swarm (project scope), then /reload-plugins.")
    print("  3. Wire credentials — see docs/credentials.md in agent-swarm. Short version:")
    print(f"     - GitHub token (env GITHUB_TOKEN) with issues+PR write on BOTH this repo and {central}.")
    print("     - In Anthropic cloud dev envs, model auth is your session; set GITHUB_TOKEN as an env var/secret.")
    print("  4. Verify dormancy: a plain `claude` session with no /swarm:* typed behaves normally.")
    if dry:
        print("\n(DRY RUN — nothing was written. Re-run without --dry-run to apply.)")


if __name__ == "__main__":
    main()
