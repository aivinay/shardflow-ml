from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShardRecord:
    path: str
    size_bytes: int
    sha256: str

    @property
    def shard_id(self) -> str:
        return self.sha256[:16]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "shard_id": self.shard_id,
        }


@dataclass(frozen=True)
class ShardManifest:
    records: list[ShardRecord]

    def shard_ids(self) -> list[str]:
        return [record.shard_id for record in self.records]

    def to_dict(self) -> dict[str, object]:
        return {
            "shard_count": len(self.records),
            "total_size_bytes": sum(record.size_bytes for record in self.records),
            "records": [record.to_dict() for record in self.records],
        }
