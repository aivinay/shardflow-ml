# ShardFlow ML

> A manifest-first way to make ML data shards reproducible, verifiable, and
> easy to distribute across workers.

[![CI](https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/aivinay/shardflow-ml/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Data pipelines often treat a directory path as if it fully describes a dataset
revision. It usually does not. ShardFlow ML records the exact shard files,
checksums, row counts, byte sizes, and worker assignments behind a run, so a
pipeline can answer practical questions later:

- Which files were included?
- Did any shard change after indexing?
- Which worker should process which shard for this seed?
- What remains after a partial run?
- What changed between two manifest revisions?

## The Core Loop

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Create and verify a manifest:

```bash
shardflow doctor --data-dir examples/data
shardflow index examples/data --output manifest.json
shardflow inspect --manifest manifest.json --format markdown
shardflow verify --manifest manifest.json
```

Plan work deterministically:

```bash
shardflow plan --manifest manifest.json --seed 42 --worker-count 2 --worker-id 0
shardflow plan --manifest manifest.json --seed 42 --worker-count 2 --all-workers
```

Resume after a partial run:

```bash
shardflow checkpoint --manifest manifest.json --checkpoint checkpoint.json
shardflow plan --manifest manifest.json --checkpoint checkpoint.json --seed 42
```

## What a Manifest Captures

| Field | Why it matters |
| --- | --- |
| `path` | Locates the shard in the indexed dataset |
| `size_bytes` | Detects file-size drift |
| `sha256` | Verifies content identity |
| `shard_id` | Stable short ID derived from the checksum |
| `row_count` | Gives text-like shards useful planning metadata |
| `media_type` | Separates JSONL, text, binary, and unknown inputs |
| `metadata` | Reserved user metadata map |

See [docs/manifest-format.md](docs/manifest-format.md) for the full schema.

## Design Guarantees

ShardFlow ML is intentionally boring in the places where data tooling should be
boring:

- File collection is deterministic.
- Shard IDs come from SHA-256 content checksums.
- Worker assignment is seed-based and repeatable.
- Checkpoints remove processed shards before planning.
- Manifests can be diffed by path, size, and checksum.
- Verification fails when files disappear or drift.

## Where It Fits

ShardFlow ML does not try to be Spark, Ray, Airflow, a data lake catalog, or a
dataset version-control system. It is the small auditable layer below those
systems: a local manifest, a verifier, and a worker-plan generator.

Typical uses:

- Preprocessing jobs that split JSONL/text shards across workers.
- Training pipelines that need a reproducible shard list.
- CI checks that guard against accidental dataset drift.
- Resume planning after interrupted data preparation.

## Reports and Commands

```bash
shardflow schema --format markdown
shardflow diff old-manifest.json new-manifest.json --format markdown
shardflow inspect --manifest manifest.json --format json
shardflow verify --manifest manifest.json
```

Output is available as JSON for automation and Markdown for review.

## Validation

The release checks cover deterministic indexing, checksums, row counts, manifest
round-trips, verification, diffs, worker partitioning, checkpoint summaries,
resume filtering, report rendering, schema output, diagnostics, and CLI commands.

```bash
python -m unittest discover -s tests
ruff check .
python -m build
shardflow doctor --data-dir examples/data
```

Container smoke:

```bash
docker build -t shardflow-ml:dev .
docker run --rm shardflow-ml:dev --version
```

## Documentation Map

- [CLI reference](docs/cli.md)
- [Manifest format](docs/manifest-format.md)
- [Architecture](docs/architecture.md)
- [Reproducibility](docs/reproducibility.md)
- [Validation notes](docs/validation.md)
- [Release checklist](docs/release.md)
- [Roadmap](docs/roadmap.md)

## Development

```bash
make install
make check
```

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md)
and [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 Vinay Gupta
