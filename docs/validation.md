# Validation Notes

Validation for the `0.1.0` release focuses on deterministic data-pipeline
metadata.

## Automated Checks

- Unit tests cover deterministic manifest ordering, checksums, row counts,
  epoch planning, worker partitioning, all-worker planning, checkpoint
  round-trips, manifest persistence, manifest verification, manifest diffing,
  manifest summaries, schema output, CLI helper commands, diagnostics, and
  resume filtering.
- CLI smoke checks cover version output, diagnostics, schema output, indexing,
  inspection, and verification.
- Ruff linting is clean.
- Source distribution and wheel builds complete successfully.

## Example Scenario

The `examples/data` directory contains two JSONL shard files. Running
`shardflow index examples/data --output manifest.json` creates a manifest with
stable shard IDs, checksums, four total rows, and aggregate byte counts.

Run:

```bash
shardflow doctor --data-dir examples/data
shardflow verify --manifest manifest.json
shardflow plan --manifest manifest.json --seed 42 --worker-count 2 --worker-id 0
shardflow inspect --manifest manifest.json --format markdown
```

These commands demonstrate the package's core reproducibility story: identify
the exact shard set, verify it has not drifted, and assign deterministic work.
