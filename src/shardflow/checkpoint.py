from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Checkpoint:
    processed: set[str] = field(default_factory=set)
    failed: dict[str, str] = field(default_factory=dict)

    def mark_processed(self, shard_id: str) -> None:
        self.processed.add(shard_id)
        self.failed.pop(shard_id, None)

    def mark_failed(self, shard_id: str, reason: str) -> None:
        if shard_id not in self.processed:
            self.failed[shard_id] = reason

    def remaining(self, shard_ids: list[str]) -> list[str]:
        return [shard_id for shard_id in shard_ids if shard_id not in self.processed]

    def summary(self, shard_ids: list[str]) -> dict[str, int]:
        remaining = self.remaining(shard_ids)
        return {
            "total": len(shard_ids),
            "processed": len(self.processed.intersection(shard_ids)),
            "failed": len([shard_id for shard_id in shard_ids if shard_id in self.failed]),
            "remaining": len(remaining),
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "processed": sorted(self.processed),
            "failed": dict(sorted(self.failed.items())),
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), indent=2, sort_keys=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            delete=False,
        ) as handle:
            handle.write(payload)
            handle.write("\n")
            tmp_path = Path(handle.name)
        tmp_path.replace(path)

    @classmethod
    def load(cls, path: Path) -> Checkpoint:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(payload)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> Checkpoint:
        return cls(
            processed=set(payload.get("processed", [])),
            failed=dict(payload.get("failed", {})),
        )
