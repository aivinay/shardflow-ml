# Release Checklist

Use this checklist before publishing a new GitHub release.

## Local Checks

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests
ruff check .
python -m build
shardflow index examples/data --output /tmp/shardflow-manifest.json
shardflow inspect --manifest /tmp/shardflow-manifest.json --format markdown
shardflow verify --manifest /tmp/shardflow-manifest.json
```

## Repository Hygiene

- README install and quickstart commands work in a clean virtual environment.
- `CHANGELOG.md` includes user-visible changes.
- `docs/manifest-format.md` matches the manifest schema.
- No secrets, local paths, or private environment values are present.
- CI is passing on supported Python versions.
