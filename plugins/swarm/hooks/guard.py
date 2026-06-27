#!/usr/bin/env python3
"""Swarm guard hook (PreToolUse).

The one hook the spec recommends registering globally (§6, §10, §12). It is a
conservative, deny-by-exception guard against the highest-blast-radius
mistakes. It is intentionally dumb and fast: it never phones home, never edits
files, and errs toward *allowing* anything it does not recognize so that plain,
non-swarm sessions stay 100% normal.

Hard guards (deny, exit 2):
  - `rm -rf` against broad / absolute / home paths
  - force-push to a protected branch (main/master/release/*)
  - history rewrites pushed to protected branches
  - writing a diff/file that carries an obvious secret
  - edits to paths outside the active worktree (when CLAUDE_WORKTREE is set)

Output contract: exit 0 = allow; exit 2 = block (stderr is shown to the model).
Any other failure mode is swallowed and treated as allow, so a buggy guard can
never wedge a session.
"""
import json
import os
import re
import sys


# --- secret signatures (intentionally narrow to avoid false positives) -------
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"(?i)aws_secret_access_key\s*=\s*\S{30,}"), "AWS secret key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub personal access token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{60,}"), "GitHub fine-grained PAT"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic API key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI-style API key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"(?i)(secret|passwd|password|token|api[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
     "hard-coded credential"),
]

PROTECTED_BRANCH = re.compile(r"\b(main|master|release(/\S+)?|prod(uction)?)\b")


def deny(reason):
    sys.stderr.write(f"[swarm-guard] BLOCKED: {reason}\n")
    sys.exit(2)


def check_bash(cmd):
    norm = " ".join(cmd.split())

    # rm -rf against broad/absolute/home targets
    if re.search(r"\brm\b[^\n]*\s-[a-zA-Z]*r[a-zA-Z]*f|\brm\b[^\n]*\s-[a-zA-Z]*f[a-zA-Z]*r", norm):
        if re.search(r"\brm\b[^\n]*\s(/|~|\$HOME|/\*|\.\s*$|\*\s*$|--no-preserve-root)", norm) \
           or re.search(r"\brm\b[^\n]*\s-[a-zA-Z]*\s+/\s*$", norm):
            deny(f"refusing destructive recursive delete of a broad/absolute path: {cmd!r}")

    # force-push to a protected branch
    if "git push" in norm and ("--force" in norm or "-f " in norm or norm.endswith(" -f") or "+refs" in norm):
        if PROTECTED_BRANCH.search(norm):
            deny(f"refusing force-push to a protected branch: {cmd!r}")

    # history rewrite + push pattern (rebase/reset then force) on protected
    if re.search(r"git push .*\+", norm) and PROTECTED_BRANCH.search(norm):
        deny(f"refusing to push a rewritten history to a protected branch: {cmd!r}")

    # secrets piped into a file or git via bash heredoc/echo
    for pat, label in SECRET_PATTERNS:
        if pat.search(cmd):
            deny(f"command appears to contain a secret ({label}); refusing")


def check_write(tool_input):
    # Combine all plausible content fields across Write/Edit/MultiEdit shapes.
    blobs = []
    for k in ("content", "new_string", "new_str"):
        v = tool_input.get(k)
        if isinstance(v, str):
            blobs.append(v)
    for edit in tool_input.get("edits", []) or []:
        if isinstance(edit, dict):
            v = edit.get("new_string") or edit.get("new_str")
            if isinstance(v, str):
                blobs.append(v)
    blob = "\n".join(blobs)
    for pat, label in SECRET_PATTERNS:
        if pat.search(blob):
            deny(f"write appears to introduce a secret ({label}); refusing")

    # edits outside the active worktree, when one is declared
    worktree = os.environ.get("CLAUDE_WORKTREE")
    path = tool_input.get("file_path") or tool_input.get("path")
    if worktree and path:
        try:
            wt = os.path.realpath(worktree)
            tgt = os.path.realpath(path if os.path.isabs(path) else os.path.join(os.getcwd(), path))
            if not (tgt == wt or tgt.startswith(wt + os.sep)):
                deny(f"refusing to edit a path outside the active worktree ({worktree}): {path}")
        except Exception:
            pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # can't parse → don't get in the way

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    try:
        if tool == "Bash":
            cmd = tool_input.get("command", "")
            if isinstance(cmd, str) and cmd:
                check_bash(cmd)
        elif tool in ("Write", "Edit", "MultiEdit"):
            check_write(tool_input)
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # never wedge a session on a guard bug

    sys.exit(0)


if __name__ == "__main__":
    main()
