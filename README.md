# ShardFlow ML

Distributed, resumable data pipeline primitives for ML training datasets.

ShardFlow ML starts with the boring pieces that make large training-data workflows dependable: shard manifests, deterministic epoch planning, worker assignment, and checkpointable progress. The goal is to grow into a practical toolkit for local, object-store, and distributed preprocessing workloads.

## Current scope

- Build deterministic shard manifests from local files.
- Compute content checksums for reproducible dataset planning.
- Create deterministic shuffled plans for each training epoch.
- Assign shards across workers without overlap.
- Persist lightweight processing checkpoints.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
```

Index a few local files:

```bash
shardflow index data/shard-000.jsonl data/shard-001.jsonl
```

## Project direction

ShardFlow ML is designed to grow toward:

- Parquet and Arrow-native shard metadata.
- Resumable preprocessing with durable checkpoints.
- Local filesystem, S3, and MinIO storage backends.
- PyTorch dataset adapters.
- Ray integration for distributed preprocessing and validation.

See [docs/roadmap.md](docs/roadmap.md) for the initial milestones.
