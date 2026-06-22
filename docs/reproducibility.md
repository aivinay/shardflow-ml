# Reproducibility

ShardFlow ML's outputs are designed to be reproducible from local files and
explicit seeds.

## Recommended Python

- Python 3.10
- Python 3.11
- Python 3.12

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Equivalent repo command:

```bash
make install
```

## Validation

```bash
python -m unittest discover -s tests
ruff check .
python -m build
shardflow doctor --data-dir examples/data
shardflow index examples/data --output /tmp/shardflow-manifest.json
shardflow verify --manifest /tmp/shardflow-manifest.json
```

## Determinism Contract

- File collection is sorted by path.
- Shard IDs derive from SHA-256 content checksums.
- Worker assignment depends on manifest records, seed, worker count, and worker
  ID.
- Checkpoint-aware planning removes processed shards before assignment.

## CI Scope

GitHub Actions runs tests, linting, package build checks, and CLI smoke checks on
Python 3.10, 3.11, and 3.12.

## Release Artifacts

Tag builds and manual workflow runs build the source distribution and wheel,
validate them with `twine check`, and upload the distribution files as workflow
artifacts.
