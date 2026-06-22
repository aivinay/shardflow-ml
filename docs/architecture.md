# Architecture

ShardFlow ML is a deterministic metadata and planning layer for local shard
files. It is intentionally dependency-light and designed for reproducible
pipeline behavior.

## Core Flow

```text
Input paths
  |
  v
File collector
  |
  v
Manifest builder
  |
  v
Manifest validator and verifier
  |
  v
Seeded planner
  |
  v
Checkpoint filter
  |
  v
JSON / Markdown reports
```

## Layers

- `index.py`: walks files and directories in deterministic order and records
  size, SHA-256 checksum, row count, and media type.
- `models.py`: defines shard records, manifests, and worker plans.
- `manifest.py`: loads, saves, validates, verifies, diffs, and filters manifests.
- `planner.py`: creates deterministic seed-based worker assignments.
- `checkpoint.py`: tracks processed and failed shard IDs.
- `reports.py`: renders summaries, schema docs, diffs, and worker plans.
- `doctor.py`: checks hashing support and optional example-data indexing.

## Boundaries

ShardFlow ML does not run distributed jobs, open network connections, mutate
dataset files, or own storage lifecycle. It creates metadata and plans that
other pipeline systems can consume.
