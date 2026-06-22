# Manifest Format

ShardFlow manifests are JSON documents with schema version
`shardflow.manifest.v1`.

```json
{
  "schema_version": "shardflow.manifest.v1",
  "shard_count": 2,
  "total_rows": 4,
  "total_size_bytes": 107,
  "records": []
}
```

Each record includes:

| Field | Description |
| --- | --- |
| `path` | Local path used to identify the shard |
| `size_bytes` | File size at indexing time |
| `sha256` | Full SHA-256 checksum |
| `shard_id` | First 16 hex characters of the checksum |
| `row_count` | Line count for text-like shard formats, otherwise null |
| `media_type` | Inferred media type |
| `metadata` | Reserved user metadata map |

## Verification

`shardflow verify --manifest manifest.json` checks that every recorded shard
still exists and that file sizes and checksums match the manifest.

## Diffing

`shardflow diff old.json new.json` reports added, removed, and changed records by
path. This is useful for describing dataset revisions across runs.

## Inspection

`shardflow inspect --manifest manifest.json` summarizes shard count, total byte
count, total rows when known, and media-type distribution.
