# ShardFlow ML

Deterministic shard manifests and worker plans for ML data pipelines.

[![CI](https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ShardFlow ML provides the small, dependable pieces that make data-preparation
workflows easier to reproduce: shard manifests, SHA-256 checksums, row counts,
media-type hints, deterministic worker assignment, manifest verification,
manifest diffs, and checkpoint progress summaries.

It is intentionally lightweight. Use it directly in local scripts, CI jobs, or
as the metadata/planning layer under larger preprocessing systems.

## What It Does

- Indexes local files and directories into deterministic shard manifests.
- Computes SHA-256 checksums and stable shard IDs.
- Infers row counts for text-like shard formats.
- Saves, loads, validates, verifies, and diffs JSON manifests.
- Creates deterministic seed-based worker plans.
- Emits single-worker or all-worker plans.
- Excludes checkpointed shards from resume plans.
- Summarizes checkpoint progress against a manifest.
- Prints manifest summaries and schema documentation from the CLI.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Get Started

Build and inspect a manifest:

```bash
shardflow index examples/data --output manifest.json
shardflow inspect --manifest manifest.json --format markdown
shardflow verify --manifest manifest.json
```

Create deterministic worker plans:

```bash
shardflow plan --manifest manifest.json --seed 42 --worker-count 2 --worker-id 0
shardflow plan --manifest manifest.json --seed 42 --worker-count 2 --all-workers
```

Use checkpoint-aware resume planning:

```bash
shardflow checkpoint --manifest manifest.json --checkpoint checkpoint.json
shardflow plan --manifest manifest.json --checkpoint checkpoint.json --seed 42
```

Compare manifest revisions:

```bash
shardflow diff old-manifest.json new-manifest.json --format markdown
```

Print the schema:

```bash
shardflow schema
```

## Why It Exists

Data pipelines often treat a directory path as if it fully describes a dataset
revision. It usually does not. ShardFlow ML records enough metadata to answer
basic operational questions:

- Which exact files were planned?
- Did any shard content drift after indexing?
- Which worker should process which shard for a given seed?
- What remains after a partial run?
- What changed between two shard manifests?

## Manifest Format

Manifests include:

| Field | Description |
| --- | --- |
| `path` | Shard path |
| `size_bytes` | File size at indexing time |
| `sha256` | Full SHA-256 checksum |
| `shard_id` | First 16 hex characters of `sha256` |
| `row_count` | Line count for text-like shards, otherwise null |
| `media_type` | Inferred media type |
| `metadata` | Reserved user metadata map |

See [docs/manifest-format.md](docs/manifest-format.md).

## Proof

The release checks are reproducible from a clean checkout:

```bash
python -m unittest discover -s tests
ruff check .
python -m build
shardflow index examples/data --output /tmp/shardflow-manifest.json
shardflow verify --manifest /tmp/shardflow-manifest.json
```

Current validation covers deterministic indexing, checksums, row counts,
manifest round-trips, manifest verification, manifest diffs, worker partitioning,
checkpoint summaries, resume filtering, report rendering, schema output, and CLI
commands. See [docs/validation.md](docs/validation.md).

## Documentation

| Start here | Go deeper |
| --- | --- |
| [CLI reference](docs/cli.md) | [Manifest format](docs/manifest-format.md) |
| [Validation notes](docs/validation.md) | [Release checklist](docs/release.md) |
| [Roadmap](docs/roadmap.md) | [Contributing](CONTRIBUTING.md) |

## Scope

ShardFlow ML is a local manifest, planning, and checkpoint utility. It does not
replace Spark, Ray, Airflow, object-store catalogs, PyTorch data loading, or
full dataset version-control systems. Its job is to provide a small auditable
layer for shard identity and work assignment.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
