# Release Checklist

Use this checklist before publishing a new GitHub release.

## Local Checks

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests
ruff check .
python -m build
shardflow doctor --data-dir examples/data
shardflow index examples/data --output /tmp/shardflow-manifest.json
shardflow inspect --manifest /tmp/shardflow-manifest.json --format markdown
shardflow verify --manifest /tmp/shardflow-manifest.json
docker build -t shardflow-ml:dev .
```

## Repository Hygiene

- README install and quickstart commands work in a clean virtual environment.
- `CHANGELOG.md` includes user-visible changes.
- `docs/manifest-format.md` matches the manifest schema.
- No secrets, local paths, or private environment values are present.
- CI is passing on supported Python versions.
- The release-artifact workflow builds and validates `dist/*` on tag pushes and
  manual workflow runs.
