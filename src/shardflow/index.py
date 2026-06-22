from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

from .models import ShardManifest, ShardRecord

_TEXT_SUFFIXES = {".csv", ".jsonl", ".ndjson", ".txt", ".tsv"}


def build_manifest(paths: Iterable[Path | str]) -> ShardManifest:
    records = [_record_for_path(path) for path in _iter_paths(paths)]
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
        row_count=_line_count(path) if path.suffix.lower() in _TEXT_SUFFIXES else None,
        media_type=_media_type(path),
    )


def _iter_paths(paths: Iterable[Path | str]) -> list[Path]:
    discovered: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            discovered.extend(sorted(child for child in path.rglob("*") if child.is_file()))
        else:
            discovered.append(path)
    return discovered


def _line_count(path: Path) -> int:
    count = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            count += chunk.count(b"\n")
    return count


def _media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "application/x-ndjson"
    if suffix == ".csv":
        return "text/csv"
    if suffix == ".tsv":
        return "text/tab-separated-values"
    if suffix == ".txt":
        return "text/plain"
    if suffix == ".parquet":
        return "application/vnd.apache.parquet"
    return "application/octet-stream"
