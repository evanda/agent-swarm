# Evals

Golden tasks per archetype (android / web / enterprise). The Improver runs these
on every inward-loop PR to confirm a proposed change to a skill, agent, or the
constitution causes **no regression** before the PR is opened (§8).

## Layout

```
evals/
├── run.py                # the harness (structural check always; LLM check when keyed)
├── router/               # golden routing fixtures (lane the rubric should pick)
├── web/                  # web-archetype golden tasks
├── android/              # android-archetype golden tasks
└── enterprise/           # enterprise-archetype golden tasks
```

## Golden task format

Each `*.json` golden task:

```json
{
  "id": "router-auth-change",
  "archetype": "router",
  "input": {
    "title": "Rotate JWT signing key",
    "body": "Swap the HS256 secret used to sign session tokens.",
    "labels": []
  },
  "expect": {
    "lane": "lane:deep",
    "risk": ["risk:auth"],
    "rationale_contains": ["auth", "session"]
  }
}
```

## Running

```bash
python3 knowledge/evals/run.py            # structural validation of all fixtures
python3 knowledge/evals/run.py --llm      # also exercise the rubric via the API
```

Without `--llm` (or `ANTHROPIC_API_KEY`) the harness only validates that every
fixture is well-formed and self-consistent — cheap enough to run in
`validate-plugin.yml`. The Improver job runs with `--llm` and a key so it can
actually exercise `route-issue` and the review rubric against expectations.
