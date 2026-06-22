# CLI Reference

ShardFlow ML exposes a small CLI for manifest creation, validation, planning,
and checkpoint inspection.

## Version

```bash
shardflow --version
```

## Doctor

```bash
shardflow doctor
shardflow doctor --data-dir examples/data --format json
```

Checks SHA-256 hashing support and, when a data directory is provided, indexes
and verifies the local shard files. Returns exit code `1` if a check fails.

## Index Shards

```bash
shardflow index examples/data --output manifest.json
```

Inputs may be files or directories. Directories are scanned recursively.

## Inspect a Manifest

```bash
shardflow inspect --manifest manifest.json
shardflow inspect --manifest manifest.json --format markdown
```

## Verify a Manifest

```bash
shardflow verify --manifest manifest.json
```

The command exits with status code `2` when files are missing or no longer match
their recorded size/checksum.

## Plan Work

```bash
shardflow plan --manifest manifest.json --seed 42 --worker-count 4 --worker-id 0
shardflow plan --manifest manifest.json --seed 42 --worker-count 4 --all-workers
shardflow plan --manifest manifest.json --checkpoint checkpoint.json --seed 42
```

## Compare Manifests

```bash
shardflow diff old.json new.json
shardflow diff old.json new.json --format markdown
```

## Checkpoint Summary

```bash
shardflow checkpoint --manifest manifest.json --checkpoint checkpoint.json
shardflow checkpoint --manifest manifest.json --checkpoint checkpoint.json --format markdown
```

## Schema

```bash
shardflow schema
shardflow schema --format json
```
