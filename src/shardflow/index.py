from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from .models import ShardManifest, ShardRecord


def build_manifest(paths: Iterable[Path | str]) -> ShardManifest:
    records = [_record_for_path(Path(path)) for path in paths]
    return ShardManifest(records=sorted(records, key=lambda record: record.path))


def _record_for_path(path: Path) -> ShardRecord:
    if not path.is_file():
        raise FileNotFoundError(f"Shard path does not exist or is not a file: {path}")

    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)

    return ShardRecord(
        path=str(path),
        size_bytes=path.stat().st_size,
        sha256=checksum.hexdigest(),
    )
