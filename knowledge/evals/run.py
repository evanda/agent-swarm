#!/usr/bin/env python3
"""Eval harness for the swarm knowledge base.

Two modes:
  - structural (default): load every golden task, assert it is well-formed and
    self-consistent. Fast, no network, runs in CI on every PR.
  - --llm: additionally exercise the live rubric (route-issue / review) against
    each fixture's expectation. Requires ANTHROPIC_API_KEY; used by improver.yml.

Exit non-zero on any failure so CI / the Improver can gate on it.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "plugins", "swarm", "scripts"))
from swarm_log import compute_frontier  # noqa: E402

VALID_LANES = {"lane:express", "lane:standard", "lane:deep"}
VALID_RISKS = {"risk:auth", "risk:data", "risk:api", "risk:money", "risk:destructive"}
REQUIRED_TOP = {"id", "archetype", "input", "expect"}


def load_fixtures():
    paths = sorted(glob.glob(os.path.join(HERE, "**", "*.json"), recursive=True))
    fixtures = []
    for p in paths:
        with open(p) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise SystemExit(f"FAIL: {p} is not valid JSON: {e}")
        fixtures.append((p, data))
    return fixtures


def validate_structure(fixtures):
    errors = []
    seen_ids = set()
    for path, fx in fixtures:
        rel = os.path.relpath(path, HERE)
        missing = REQUIRED_TOP - set(fx)
        if missing:
            errors.append(f"{rel}: missing keys {sorted(missing)}")
            continue
        if fx["id"] in seen_ids:
            errors.append(f"{rel}: duplicate id {fx['id']!r}")
        seen_ids.add(fx["id"])
        expect = fx.get("expect", {})
        lane = expect.get("lane")
        if lane and lane not in VALID_LANES:
            errors.append(f"{rel}: unknown lane {lane!r}")
        for r in expect.get("risk", []) or []:
            if r not in VALID_RISKS:
                errors.append(f"{rel}: unknown risk flag {r!r}")
        if not isinstance(fx.get("input"), dict):
            errors.append(f"{rel}: 'input' must be an object")
            continue
        if fx["archetype"] == "resume" and "frontier_tasks" in expect:
            errors += validate_resume_frontier(rel, fx)
    return errors


def validate_resume_frontier(rel, fx):
    """resume-cycle's frontier reconcile (Step 3) is enforced code
    (swarm_log.compute_frontier), not just model-followed instructions — assert
    it against each resume fixture's structured events + ground truth so a
    regression here fails CI structurally (issue #11)."""
    inp = fx["input"]
    events = inp.get("events")
    if not events:
        return [f"{rel}: archetype 'resume' with frontier_tasks needs 'input.events' "
                f"(structured events, not just the human-readable summary)"]
    frontier, _notes = compute_frontier(events, inp.get("ground_truth"))
    expected = fx["expect"]["frontier_tasks"]
    if frontier != expected:
        return [f"{rel}: compute_frontier produced {frontier}, expected {expected}"]
    return []


def run_llm(fixtures):
    """Placeholder for the live rubric check.

    Intentionally a clear extension point: wire this to the Anthropic SDK and
    feed each fixture's input through the route-issue / review rubric, then
    compare against `expect`. Kept inert here so the structural path stays
    dependency-free; improver.yml installs the SDK and supplies the key.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("--llm requested but ANTHROPIC_API_KEY is unset; skipping live checks.")
        return []
    print(f"(llm) would exercise {len(fixtures)} fixtures against the live rubric.")
    print("(llm) harness wiring is a TODO — see knowledge/evals/README.md.")
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="also run live rubric checks")
    args = ap.parse_args()

    fixtures = load_fixtures()
    if not fixtures:
        print("No fixtures found.")
        return 0

    errors = validate_structure(fixtures)
    if args.llm:
        errors += run_llm(fixtures)

    if errors:
        print(f"\n{len(errors)} eval failure(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(fixtures)} golden task(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
