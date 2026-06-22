from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .checkpoint import Checkpoint
from .models import ShardManifest, ShardRecord


def save_manifest(manifest: ShardManifest, path: Path) -> None:
    path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(path: Path) -> ShardManifest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ShardManifest.from_dict(payload)


def validate_manifest(manifest: ShardManifest) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    seen_paths: set[str] = set()
    if manifest.schema_version != "shardflow.manifest.v1":
        errors.append(f"Unsupported schema version: {manifest.schema_version}")
    for record in manifest.records:
        if record.shard_id in seen:
            errors.append(f"Duplicate shard id: {record.shard_id}")
        seen.add(record.shard_id)
        if record.path in seen_paths:
            errors.append(f"Duplicate shard path: {record.path}")
        seen_paths.add(record.path)
        if record.size_bytes < 0:
            errors.append(f"Negative size for shard: {record.path}")
        if len(record.sha256) != 64:
            errors.append(f"Invalid sha256 for shard: {record.path}")
        if record.row_count is not None and record.row_count < 0:
            errors.append(f"Negative row count for shard: {record.path}")
    return errors


def verify_manifest(manifest: ShardManifest) -> list[str]:
    errors = validate_manifest(manifest)
    for record in manifest.records:
        path = Path(record.path)
        if not path.is_file():
            errors.append(f"Missing shard path: {record.path}")
            continue
        size_bytes = path.stat().st_size
        if size_bytes != record.size_bytes:
            errors.append(
                f"Size mismatch for {record.path}: expected {record.size_bytes}, "
                f"found {size_bytes}"
            )
        sha256 = _sha256(path)
        if sha256 != record.sha256:
            errors.append(
                f"Checksum mismatch for {record.path}: expected {record.sha256}, found {sha256}"
            )
    return errors


def diff_manifests(
    baseline: ShardManifest,
    candidate: ShardManifest,
) -> dict[str, list[dict[str, object]]]:
    baseline_by_path = {record.path: record for record in baseline.records}
    candidate_by_path = {record.path: record for record in candidate.records}

    added = [
        candidate_by_path[path].to_dict()
        for path in sorted(candidate_by_path.keys() - baseline_by_path.keys())
    ]
    removed = [
        baseline_by_path[path].to_dict()
        for path in sorted(baseline_by_path.keys() - candidate_by_path.keys())
    ]
    changed = [
        {
            "path": path,
            "baseline": baseline_by_path[path].to_dict(),
            "candidate": candidate_by_path[path].to_dict(),
        }
        for path in sorted(baseline_by_path.keys() & candidate_by_path.keys())
        if baseline_by_path[path].sha256 != candidate_by_path[path].sha256
        or baseline_by_path[path].size_bytes != candidate_by_path[path].size_bytes
    ]
    return {"added": added, "removed": removed, "changed": changed}


def remaining_records(manifest: ShardManifest, checkpoint: Checkpoint) -> list[ShardRecord]:
    return [record for record in manifest.records if record.shard_id not in checkpoint.processed]


def _sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()
