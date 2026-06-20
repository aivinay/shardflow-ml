from __future__ import annotations

import json
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

    def save(self, path: Path) -> None:
        payload = {
            "processed": sorted(self.processed),
            "failed": dict(sorted(self.failed.items())),
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Checkpoint":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            processed=set(payload.get("processed", [])),
            failed=dict(payload.get("failed", {})),
        )
