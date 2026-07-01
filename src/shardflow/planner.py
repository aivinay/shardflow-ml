from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from .models import ShardRecord


@dataclass(frozen=True)
class WorkerPlan:
    seed: int
    worker_count: int
    worker_id: int
    records: list[ShardRecord]

    def shard_ids(self) -> list[str]:
        return [record.shard_id for record in self.records]

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "worker_count": self.worker_count,
            "worker_id": self.worker_id,
            "shard_count": len(self.records),
            "total_size_bytes": sum(record.size_bytes for record in self.records),
            "shards": [record.to_dict() for record in self.records],
        }


def plan_epoch(
    records: Sequence[ShardRecord],
    *,
    seed: int,
    worker_count: int = 1,
    worker_id: int = 0,
) -> list[ShardRecord]:
    if worker_count <= 0:
        raise ValueError("worker_count must be positive")
    if worker_id < 0 or worker_id >= worker_count:
        raise ValueError("worker_id must be in the range [0, worker_count)")

    ordered = list(records)
    # Deterministic planning seed; this is not cryptographic randomness.
    random.Random(seed).shuffle(ordered)  # nosec B311
    return [
        record
        for index, record in enumerate(ordered)
        if index % worker_count == worker_id
    ]


def build_worker_plan(
    records: Sequence[ShardRecord],
    *,
    seed: int,
    worker_count: int = 1,
    worker_id: int = 0,
) -> WorkerPlan:
    return WorkerPlan(
        seed=seed,
        worker_count=worker_count,
        worker_id=worker_id,
        records=plan_epoch(records, seed=seed, worker_count=worker_count, worker_id=worker_id),
    )


def plan_all_workers(
    records: Sequence[ShardRecord],
    *,
    seed: int,
    worker_count: int,
) -> dict[int, WorkerPlan]:
    return {
        worker_id: build_worker_plan(
            records,
            seed=seed,
            worker_count=worker_count,
            worker_id=worker_id,
        )
        for worker_id in range(worker_count)
    }
