#!/usr/bin/env python3
"""Bump the swarm plugin version and keep the consumer pin in lockstep.

The plugin is only consumable when plugin.json's version and the consumer
template's pinned `ref` agree (validate_plugin.py enforces this at PR time; the
release workflow tags + publishes on merge). This is the single command that
moves both, so no human — and no agent — has to remember the second edit.

Usage:
    python3 scripts/bump_version.py            # patch: 0.2.4 -> 0.2.5
    python3 scripts/bump_version.py --minor    # 0.2.4 -> 0.3.0
    python3 scripts/bump_version.py --major     # 0.2.4 -> 1.0.0
    python3 scripts/bump_version.py --set 0.5.0 # explicit

Edits are targeted string replacements, so the diff is exactly two lines.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins/swarm/.claude-plugin/plugin.json")
CONSUMER = os.path.join(ROOT, "templates/consumer/settings.json")


def read(path):
    with open(path) as f:
        return f.read()


def current_version():
    m = re.search(r'"version":\s*"(\d+)\.(\d+)\.(\d+)"', read(PLUGIN))
    if not m:
        sys.exit("error: could not find a semver \"version\" in plugin.json")
    return tuple(int(g) for g in m.groups())


def main(argv):
    part = "patch"
    explicit = None
    for a in argv:
        if a == "--major":
            part = "major"
        elif a == "--minor":
            part = "minor"
        elif a == "--patch":
            part = "patch"
        elif a == "--set":
            explicit = argv[argv.index(a) + 1]
        elif a.startswith("--set="):
            explicit = a.split("=", 1)[1]

    major, minor, patch = current_version()
    old = f"{major}.{minor}.{patch}"

    if explicit:
        if not re.fullmatch(r"\d+\.\d+\.\d+", explicit):
            sys.exit(f"error: --set expects X.Y.Z, got '{explicit}'")
        new = explicit
    elif part == "major":
        new = f"{major + 1}.0.0"
    elif part == "minor":
        new = f"{major}.{minor + 1}.0"
    else:
        new = f"{major}.{minor}.{patch + 1}"

    if new == old:
        sys.exit(f"error: new version {new} equals current version")

    # plugin.json: replace the version string.
    plugin_txt = read(PLUGIN)
    plugin_txt, n1 = re.subn(
        r'("version":\s*")' + re.escape(old) + r'(")',
        r"\g<1>" + new + r"\g<2>", plugin_txt, count=1)
    if n1 != 1:
        sys.exit("error: failed to rewrite plugin.json version")
    with open(PLUGIN, "w") as f:
        f.write(plugin_txt)

    # consumer template: replace the pinned ref (v-prefixed).
    consumer_txt = read(CONSUMER)
    consumer_txt, n2 = re.subn(
        r'("ref":\s*")v\d+\.\d+\.\d+(")',
        r"\g<1>v" + new + r"\g<2>", consumer_txt, count=1)
    if n2 != 1:
        sys.exit("error: failed to rewrite consumer template ref")
    with open(CONSUMER, "w") as f:
        f.write(consumer_txt)

    print(f"bumped {old} -> {new}")
    print(f"  plugins/swarm/.claude-plugin/plugin.json  version -> {new}")
    print(f"  templates/consumer/settings.json          ref     -> v{new}")
    print("On merge, .github/workflows/release.yml tags + publishes "
          f"v{new} automatically.")


if __name__ == "__main__":
    main(sys.argv[1:])
