#!/usr/bin/env python3
"""Swarm version-check hook (UserPromptSubmit).

Advisory only — never blocks, never edits anything, and stays out of the way
of plain (non-swarm) sessions. Bails instantly on any prompt that doesn't
start with `/swarm:`, so it costs nothing outside of swarm use. Only for a
`/swarm:*` prompt does it compare the plugin version actually running
(`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`) against the central
repo's latest release, and only then may it make a network call — cached with
a TTL so it doesn't hit GitHub on every single swarm command in a session.

Output contract: always exit 0 (advisory, never blocking). On a stale pin,
print a JSON object with `systemMessage`/`additionalContext` so the human and
the model both see the nudge; otherwise print nothing. Any failure (no
`.swarm/config.json`, `gh` unavailable, offline, malformed cache) is swallowed
silently — the hook must never wedge or spam a session.
"""
import json
import os
import subprocess
import sys
import time

CACHE_TTL_SECONDS = 24 * 60 * 60  # once a day is plenty for an advisory nudge
NETWORK_TIMEOUT_SECONDS = 4


def read_json(path):
    with open(path) as f:
        return json.load(f)


def current_version():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        return None
    manifest = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    return read_json(manifest).get("version")


def central_repo(cwd):
    cfg_path = os.path.join(cwd, ".swarm", "config.json")
    if not os.path.exists(cfg_path):
        return None
    return read_json(cfg_path).get("central_repo")


def cached_latest(cwd):
    """Return a cached latest-version string if the cache is fresh, else None."""
    cache_path = os.path.join(cwd, ".swarm", "version-check-cache.json")
    if not os.path.exists(cache_path):
        return None
    data = read_json(cache_path)
    checked_at = data.get("checked_at", 0)
    if time.time() - checked_at > CACHE_TTL_SECONDS:
        return None
    return data.get("latest")


def write_cache(cwd, latest):
    cache_path = os.path.join(cwd, ".swarm", "version-check-cache.json")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump({"checked_at": time.time(), "latest": latest}, f)


def fetch_latest(repo):
    out = subprocess.run(
        ["gh", "release", "view", "--repo", repo, "--json", "tagName", "-q", ".tagName"],
        capture_output=True, text=True, timeout=NETWORK_TIMEOUT_SECONDS,
    )
    if out.returncode != 0:
        return None
    tag = out.stdout.strip()
    return tag or None


def normalize(v):
    return (v or "").lstrip("v")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = payload.get("userPrompt") or ""
    if not isinstance(prompt, str) or not prompt.lstrip().startswith("/swarm:"):
        sys.exit(0)  # not a swarm command — stay out of the way, no network call

    cwd = payload.get("cwd") or os.getcwd()

    try:
        current = current_version()
        if not current:
            sys.exit(0)

        latest = cached_latest(cwd)
        if latest is None:
            repo = central_repo(cwd)
            if not repo:
                sys.exit(0)  # swarm isn't installed here; nothing to advise on
            latest = fetch_latest(repo)
            if latest is None:
                sys.exit(0)  # offline / gh unavailable / rate-limited — stay silent
            write_cache(cwd, latest)

        if normalize(current) != normalize(latest):
            msg = (f"swarm plugin is on v{normalize(current)}; "
                   f"latest is {latest} — run /swarm:update to upgrade.")
            print(json.dumps({
                "systemMessage": msg,
                "additionalContext": (
                    f"[swarm-version-check] {msg} This is advisory only — the "
                    f"current command proceeds normally; the human can run "
                    f"/swarm:update whenever they choose."
                ),
            }))
    except Exception:
        pass  # never let an advisory hook wedge or fail a session

    sys.exit(0)


if __name__ == "__main__":
    main()
