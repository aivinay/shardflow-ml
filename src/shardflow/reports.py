from __future__ import annotations

import json
from collections import Counter

from .manifest import diff_manifests
from .models import ShardManifest
from .planner import WorkerPlan


def manifest_summary(manifest: ShardManifest) -> dict[str, object]:
    media_types = Counter(record.media_type for record in manifest.records)
    return {
        "schema_version": manifest.schema_version,
        "shard_count": len(manifest.records),
        "total_size_bytes": sum(record.size_bytes for record in manifest.records),
        "total_rows": _sum_optional(record.row_count for record in manifest.records),
        "media_types": dict(sorted(media_types.items())),
    }


def manifest_summary_json(manifest: ShardManifest) -> str:
    return json.dumps(manifest_summary(manifest), indent=2, sort_keys=True)


def manifest_summary_markdown(manifest: ShardManifest) -> str:
    summary = manifest_summary(manifest)
    lines = [
        "# ShardFlow Manifest Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Schema version | {summary['schema_version']} |",
        f"| Shards | {summary['shard_count']} |",
        f"| Total bytes | {summary['total_size_bytes']} |",
        f"| Total rows | {summary['total_rows'] if summary['total_rows'] is not None else '-'} |",
        "",
        "## Media Types",
        "",
        "| Media type | Shards |",
        "| --- | ---: |",
    ]
    for media_type, count in summary["media_types"].items():
        lines.append(f"| {media_type} | {count} |")
    return "\n".join(lines) + "\n"


def diff_to_json(baseline: ShardManifest, candidate: ShardManifest) -> str:
    return json.dumps(diff_manifests(baseline, candidate), indent=2, sort_keys=True)


def diff_to_markdown(baseline: ShardManifest, candidate: ShardManifest) -> str:
    diff = diff_manifests(baseline, candidate)
    lines = [
        "# ShardFlow Manifest Diff",
        "",
        "| Category | Count |",
        "| --- | ---: |",
        f"| Added | {len(diff['added'])} |",
        f"| Removed | {len(diff['removed'])} |",
        f"| Changed | {len(diff['changed'])} |",
    ]
    for category in ("added", "removed", "changed"):
        if not diff[category]:
            continue
        lines.extend(["", f"## {category.title()}", ""])
        for item in diff[category]:
            path = item["path"] if category == "changed" else item["path"]
            lines.append(f"- `{path}`")
    return "\n".join(lines) + "\n"


def worker_plan_json(plan: WorkerPlan) -> str:
    return json.dumps(plan.to_dict(), indent=2, sort_keys=True)


def worker_plan_markdown(plan: WorkerPlan) -> str:
    lines = [
        "# ShardFlow Worker Plan",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Seed | {plan.seed} |",
        f"| Worker | {plan.worker_id} / {plan.worker_count} |",
        f"| Shards | {len(plan.records)} |",
        f"| Total bytes | {sum(record.size_bytes for record in plan.records)} |",
        "",
        "| Shard ID | Path | Bytes | Rows | Media type |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for record in plan.records:
        rows = record.row_count if record.row_count is not None else "-"
        lines.append(
            f"| `{record.shard_id}` | `{record.path}` | {record.size_bytes} | "
            f"{rows} | {record.media_type} |"
        )
    return "\n".join(lines) + "\n"


def all_worker_plans_json(plans: dict[int, WorkerPlan]) -> str:
    return json.dumps(
        {str(worker_id): plan.to_dict() for worker_id, plan in sorted(plans.items())},
        indent=2,
        sort_keys=True,
    )


def manifest_schema_json() -> str:
    return json.dumps(
        {
            "schema_version": "shardflow.manifest.v1",
            "record_fields": {
                "path": "Shard path.",
                "size_bytes": "File size at indexing time.",
                "sha256": "Full SHA-256 checksum.",
                "shard_id": "First 16 hex characters of sha256.",
                "row_count": "Line count for text-like shards, otherwise null.",
                "media_type": "Inferred media type.",
                "metadata": "Reserved user metadata map.",
            },
        },
        indent=2,
        sort_keys=True,
    )


def manifest_schema_markdown() -> str:
    return """# ShardFlow Manifest Schema

Schema version: `shardflow.manifest.v1`

| Field | Description |
| --- | --- |
| `path` | Shard path |
| `size_bytes` | File size at indexing time |
| `sha256` | Full SHA-256 checksum |
| `shard_id` | First 16 hex characters of `sha256` |
| `row_count` | Line count for text-like shards, otherwise null |
| `media_type` | Inferred media type |
| `metadata` | Reserved user metadata map |
"""


def _sum_optional(values: object) -> int | None:
    materialized = list(values)
    if any(value is None for value in materialized):
        return None
    return int(sum(materialized))
