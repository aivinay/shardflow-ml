from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ShardRecord:
    path: str
    size_bytes: int
    sha256: str
    row_count: int | None = None
    media_type: str = "application/octet-stream"
    metadata: Mapping[str, object] = field(default_factory=dict)

    @property
    def shard_id(self) -> str:
        return self.sha256[:16]

    def __hash__(self) -> int:
        return hash((self.path, self.sha256))

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "shard_id": self.shard_id,
            "row_count": self.row_count,
            "media_type": self.media_type,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ShardRecord:
        return cls(
            path=str(payload["path"]),
            size_bytes=int(payload["size_bytes"]),
            sha256=str(payload["sha256"]),
            row_count=_optional_int(payload.get("row_count")),
            media_type=str(payload.get("media_type", "application/octet-stream")),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class ShardManifest:
    records: list[ShardRecord]
    schema_version: str = "shardflow.manifest.v1"

    def shard_ids(self) -> list[str]:
        return [record.shard_id for record in self.records]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "shard_count": len(self.records),
            "total_size_bytes": sum(record.size_bytes for record in self.records),
            "total_rows": _sum_optional(record.row_count for record in self.records),
            "records": [record.to_dict() for record in self.records],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ShardManifest:
        records = [ShardRecord.from_dict(record) for record in payload.get("records", [])]
        return cls(
            records=records,
            schema_version=str(payload.get("schema_version", "shardflow.manifest.v1")),
        )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


def _sum_optional(values: object) -> int | None:
    materialized = list(values)
    if any(value is None for value in materialized):
        return None
    return int(sum(materialized))
