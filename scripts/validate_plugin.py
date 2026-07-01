#!/usr/bin/env python3
"""Validate the swarm marketplace + plugin structure.

Run locally or in CI (validate-plugin.yml). Checks:
  - marketplace.json / plugin.json parse and carry required keys
  - every plugin source referenced by the marketplace exists
  - every agent / skill / command markdown file has YAML frontmatter
  - entry commands are explicit-only (disable-model-invocation: true)
  - operational skills are agent-invoked (user-invocable: false)
  - hooks.json parses and referenced hook scripts exist
  - python helpers compile

Exit non-zero on any problem.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warnings = []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def load_json(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        err(f"missing file: {rel}")
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        err(f"{rel}: invalid JSON: {e}")
        return None


def frontmatter(path):
    """Return the YAML frontmatter block as a dict-ish of top-level keys."""
    with open(path) as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm


# --- marketplace + plugin manifests -----------------------------------------
mkt = load_json(".claude-plugin/marketplace.json")
if mkt is not None:
    for key in ("name", "owner", "plugins"):
        if key not in mkt:
            err(f"marketplace.json: missing '{key}'")
    for p in mkt.get("plugins", []):
        src = p.get("source", "")
        if src.startswith("./"):
            if not os.path.isdir(os.path.join(ROOT, src)):
                err(f"marketplace.json: plugin source not found: {src}")

plugin = load_json("plugins/swarm/.claude-plugin/plugin.json")
if plugin is not None:
    for key in ("name", "version", "description"):
        if key not in plugin:
            err(f"plugin.json: missing '{key}'")

# --- version <-> consumer-template pin sync ---------------------------------
# The plugin is only consumable when four artifacts agree: plugin.json version,
# the git tag, the GitHub release, and the consumer template's pinned ref. Tag +
# release are created post-merge by .github/workflows/release.yml; the piece we
# can enforce at PR time is that the template ref matches the version being
# shipped, so a version bump can't merge without moving the adoption pin too.
if plugin is not None and "version" in plugin:
    expected_ref = f"v{plugin['version']}"
    consumer = load_json("templates/consumer/settings.json")
    if consumer is not None:
        try:
            ref = consumer["extraKnownMarketplaces"]["swarm"]["source"]["ref"]
        except (KeyError, TypeError):
            ref = None
            err("templates/consumer/settings.json: missing "
                "extraKnownMarketplaces.swarm.source.ref")
        if ref is not None and ref != expected_ref:
            err(f"version pin out of sync: templates/consumer/settings.json ref "
                f"'{ref}' != plugin.json version '{expected_ref}'. Bump both in the "
                f"same PR (the release workflow tags + publishes {expected_ref} on merge).")

# --- agents -----------------------------------------------------------------
EXPECTED_AGENTS = {
    "orchestrator", "explorer", "architect", "challenger", "implementer",
    "reviewer", "integrator", "scribe", "improver", "scout",
}
agents_dir = os.path.join(ROOT, "plugins/swarm/agents")
found_agents = set()
for fn in os.listdir(agents_dir) if os.path.isdir(agents_dir) else []:
    if not fn.endswith(".md"):
        continue
    fm = frontmatter(os.path.join(agents_dir, fn))
    if not fm:
        err(f"agents/{fn}: missing frontmatter")
        continue
    if "name" not in fm or "description" not in fm:
        err(f"agents/{fn}: frontmatter needs name + description")
    found_agents.add(fm.get("name", fn[:-3]))
missing_agents = EXPECTED_AGENTS - found_agents
if missing_agents:
    err(f"missing agents: {sorted(missing_agents)}")

# --- skills -----------------------------------------------------------------
skills_dir = os.path.join(ROOT, "plugins/swarm/skills")
for d in os.listdir(skills_dir) if os.path.isdir(skills_dir) else []:
    sp = os.path.join(skills_dir, d, "SKILL.md")
    if not os.path.exists(sp):
        err(f"skills/{d}: missing SKILL.md")
        continue
    fm = frontmatter(sp)
    if not fm or "name" not in fm or "description" not in fm:
        err(f"skills/{d}/SKILL.md: frontmatter needs name + description")
        continue
    if fm.get("user-invocable", "").lower() != "false":
        warn(f"skills/{d}: operational skills should set user-invocable: false")

# --- commands (entry points must be explicit-only) --------------------------
cmd_dir = os.path.join(ROOT, "plugins/swarm/commands")
EXPECTED_CMDS = {"start", "express", "retro", "status", "help", "stop", "improve", "scout"}
found_cmds = set()
for fn in os.listdir(cmd_dir) if os.path.isdir(cmd_dir) else []:
    if not fn.endswith(".md"):
        continue
    found_cmds.add(fn[:-3])
    fm = frontmatter(os.path.join(cmd_dir, fn))
    if not fm:
        err(f"commands/{fn}: missing frontmatter")
        continue
    if fm.get("disable-model-invocation", "").lower() != "true":
        err(f"commands/{fn}: entry commands must set disable-model-invocation: true")
missing_cmds = EXPECTED_CMDS - found_cmds
if missing_cmds:
    err(f"missing entry commands: {sorted(missing_cmds)}")

# --- hooks ------------------------------------------------------------------
hooks = load_json("plugins/swarm/hooks/hooks.json")
if hooks is not None:
    blob = json.dumps(hooks)
    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/(\S+?\.py)", blob):
        if not os.path.exists(os.path.join(ROOT, "plugins/swarm", ref)):
            err(f"hooks.json references missing script: {ref}")

# --- python helpers compile -------------------------------------------------
import py_compile  # noqa: E402
for rel in ("plugins/swarm/hooks/guard.py", "knowledge/evals/run.py",
            "scripts/validate_plugin.py", "scripts/install.py",
            "plugins/swarm/scripts/swarm_log.py"):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        try:
            py_compile.compile(p, doraise=True)
        except py_compile.PyCompileError as e:
            err(f"{rel}: does not compile: {e}")

# --- report -----------------------------------------------------------------
for w in warnings:
    print(f"WARN: {w}")
if errors:
    print(f"\n{len(errors)} validation error(s):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"OK: marketplace + plugin valid ({len(found_agents)} agents, entry commands explicit-only).")
