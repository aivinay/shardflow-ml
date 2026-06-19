from __future__ import annotations

import random
from typing import Sequence

from .models import ShardRecord


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
    random.Random(seed).shuffle(ordered)
    return [
        record
        for index, record in enumerate(ordered)
        if index % worker_count == worker_id
    ]
