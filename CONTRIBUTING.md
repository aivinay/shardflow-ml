# Contributing

Thank you for considering a contribution to ShardFlow ML.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m unittest discover -s tests
ruff check .
```

## Contribution guidelines

- Preserve deterministic planning behavior.
- Add tests for manifest, planner, and checkpoint changes.
- Avoid backend-specific assumptions in core models.
- Keep manifest schemas backward compatible where possible.
