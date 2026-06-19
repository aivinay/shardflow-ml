# Roadmap

## Milestone 1: Local Shard Planning

- Build manifests from local files.
- Compute file size and SHA-256 checksums.
- Add deterministic epoch shuffling.
- Split shard plans across workers.

## Milestone 2: Checkpointed Preprocessing

- Persist processed shard state.
- Resume interrupted runs.
- Track failed shards and retry attempts.
- Emit machine-readable run summaries.

## Milestone 3: ML Storage Formats

- Add Parquet metadata extraction.
- Add Arrow schema summaries.
- Support JSONL-to-Parquet preprocessing examples.

## Milestone 4: Distributed Execution

- Add Ray-backed workers.
- Add S3 and MinIO storage adapters.
- Provide PyTorch dataset integration.
