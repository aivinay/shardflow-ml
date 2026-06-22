<h1 align="center">ShardFlow ML</h1>

<p align="center"><strong>Deterministic shard manifests and worker plans for ML data pipelines.</strong></p>

<p align="center">
  <a href="https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml"><img src="https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="#get-started">Install</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#proof">Proof</a> ·
  <a href="#privacy-and-scope">Privacy</a> ·
  <a href="docs/">Docs</a>
</p>

---

> ShardFlow ML records the exact local files that make up a dataset revision,
> verifies their content with checksums, and creates deterministic worker plans
> for distributed preprocessing or training jobs.

It is the small metadata layer missing from many data-prep scripts: shard IDs,
sizes, SHA-256 checksums, row counts, media-type hints, resumable checkpoints,
manifest diffs, and stable seed-based partitioning.

## What It Does

- Indexes local files and directories into deterministic shard manifests.
- Computes SHA-256 checksums and stable shard IDs.
- Infers row counts for text-like shard formats.
- Saves, loads, validates, verifies, and diffs JSON manifests.
- Creates deterministic single-worker and all-worker plans.
- Excludes checkpointed shards from resume plans.
- Summarizes checkpoint progress against a manifest.
- Provides schema docs, Markdown reports, and `doctor` diagnostics.

## How It Works

```text
Dataset files/directories
  |
  v
Indexer: stable ordering, size, checksum, row count, media type
  |
  v
Manifest: JSON schema version, shard metadata, aggregate counts
  |
  v
Planner: deterministic seeded shuffle and worker partitioning
  |
  v
Checkpoint filter: processed shards removed from resume plans
  |
  v
Reports: summary, schema, diff, worker plans, verification status
```

The core invariant: the same files, seed, worker count, and checkpoint state
produce the same plan.

## Get Started

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

```bash
shardflow doctor --data-dir examples/data
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

Container smoke check:

```bash
docker build -t shardflow-ml:dev .
docker run --rm shardflow-ml:dev --version
```

## Proof

The current release is validated with unit tests, linting, package build checks,
CLI smoke checks, manifest verification, and a release-artifact workflow.

```bash
python -m unittest discover -s tests
ruff check .
python -m build
shardflow doctor --data-dir examples/data
shardflow index examples/data --output /tmp/shardflow-manifest.json
shardflow verify --manifest /tmp/shardflow-manifest.json
```

Validation covers deterministic indexing, checksums, row counts, manifest
round-trips, manifest verification, diffs, worker partitioning, checkpoint
summaries, resume filtering, report rendering, schema output, diagnostics, and
CLI commands. See [docs/validation.md](docs/validation.md).

## Manifest Format

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

## Privacy and Scope

ShardFlow ML reads local file metadata and file bytes only to compute sizes,
row counts, and checksums. It does not upload datasets, send telemetry, or store
data outside the manifest/checkpoint files you choose to write.

It does not replace Spark, Ray, Airflow, object-store catalogs, PyTorch data
loading, or full dataset version-control systems. Its job is a small auditable
layer for shard identity, verification, and work assignment.

## Documentation

| Start here | Go deeper |
| --- | --- |
| [CLI reference](docs/cli.md) | [Manifest format](docs/manifest-format.md) |
| [Architecture](docs/architecture.md) | [Reproducibility](docs/reproducibility.md) |
| [Validation notes](docs/validation.md) | [Release checklist](docs/release.md) |
| [Roadmap](docs/roadmap.md) | [Contributing](CONTRIBUTING.md) |

## Development

```bash
make install
make check
```

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md)
and [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 Vinay Gupta
