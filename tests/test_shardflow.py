import json
import tempfile
import unittest
from pathlib import Path

from shardflow import (
    Checkpoint,
    build_manifest,
    build_worker_plan,
    diff_manifests,
    load_manifest,
    manifest_summary,
    plan_all_workers,
    plan_epoch,
    remaining_records,
    save_manifest,
    validate_manifest,
    verify_manifest,
)
from shardflow.cli import run
from shardflow.models import ShardManifest, ShardRecord
from shardflow.reports import (
    diff_to_markdown,
    manifest_schema_markdown,
    manifest_summary_markdown,
    worker_plan_markdown,
)


class ShardFlowTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_checksummed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            second = root / "b.jsonl"
            first = root / "a.jsonl"
            second.write_text("second\n", encoding="utf-8")
            first.write_text("first\n", encoding="utf-8")

            manifest = build_manifest([second, first])

            self.assertEqual(
                [Path(record.path).name for record in manifest.records],
                ["a.jsonl", "b.jsonl"],
            )
            self.assertEqual(manifest.to_dict()["shard_count"], 2)
            self.assertEqual(manifest.to_dict()["total_rows"], 2)
            self.assertEqual(manifest_summary(manifest)["media_types"], {"application/x-ndjson": 2})
            self.assertTrue(all(len(record.sha256) == 64 for record in manifest.records))

    def test_epoch_plans_are_repeatable_and_partitioned(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = []
            for index in range(6):
                path = root / f"shard-{index}.jsonl"
                path.write_text(f"{index}\n", encoding="utf-8")
                paths.append(path)

            manifest = build_manifest(paths)
            first_plan = plan_epoch(manifest.records, seed=42, worker_count=2, worker_id=0)
            second_plan = plan_epoch(manifest.records, seed=42, worker_count=2, worker_id=0)
            other_worker = plan_epoch(manifest.records, seed=42, worker_count=2, worker_id=1)

            self.assertEqual(first_plan, second_plan)
            self.assertTrue(set(first_plan).isdisjoint(set(other_worker)))
            self.assertEqual(len(first_plan) + len(other_worker), len(manifest.records))
            worker_plan = build_worker_plan(manifest.records, seed=42, worker_count=2, worker_id=0)
            self.assertEqual(worker_plan.shard_ids(), [record.shard_id for record in first_plan])
            all_plans = plan_all_workers(manifest.records, seed=42, worker_count=2)
            self.assertEqual(set(all_plans), {0, 1})

    def test_checkpoint_roundtrip_tracks_remaining_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            checkpoint = Checkpoint()
            checkpoint.mark_processed("shard-a")
            checkpoint.mark_failed("shard-b", "decode error")
            checkpoint.save(path)

            loaded = Checkpoint.load(path)

            self.assertEqual(
                loaded.remaining(["shard-a", "shard-b", "shard-c"]),
                ["shard-b", "shard-c"],
            )
            self.assertEqual(loaded.failed, {"shard-b": "decode error"})
            self.assertEqual(loaded.summary(["shard-a", "shard-b", "shard-c"])["remaining"], 2)

    def test_manifest_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            shard = root / "shard.jsonl"
            shard.write_text('{"text":"hello"}\n', encoding="utf-8")
            path = root / "manifest.json"

            manifest = build_manifest([shard])
            save_manifest(manifest, path)
            loaded = load_manifest(path)

            self.assertEqual(
                json.dumps(loaded.to_dict(), sort_keys=True),
                json.dumps(manifest.to_dict(), sort_keys=True),
            )

    def test_verify_manifest_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            shard = root / "shard.jsonl"
            shard.write_text("before\n", encoding="utf-8")
            manifest = build_manifest([shard])

            self.assertEqual(verify_manifest(manifest), [])

            shard.write_text("after\n", encoding="utf-8")
            errors = verify_manifest(manifest)

            self.assertTrue(any("Checksum mismatch" in error for error in errors))

    def test_manifest_diff_and_resume_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "a.jsonl"
            second = root / "b.jsonl"
            first.write_text("a\n", encoding="utf-8")
            second.write_text("b\n", encoding="utf-8")
            baseline = build_manifest([first])
            candidate = build_manifest([first, second])
            checkpoint = Checkpoint(processed={baseline.records[0].shard_id})

            diff = diff_manifests(baseline, candidate)

            self.assertEqual(len(diff["added"]), 1)
            self.assertEqual(remaining_records(candidate, checkpoint), [candidate.records[1]])

    def test_manifest_validation_catches_schema_and_duplicate_paths(self) -> None:
        record = ShardRecord(path="a.jsonl", size_bytes=1, sha256="a" * 64, row_count=1)
        manifest = ShardManifest(
            records=[record, record],
            schema_version="unknown",
        )

        errors = validate_manifest(manifest)

        self.assertTrue(any("Unsupported schema version" in error for error in errors))
        self.assertTrue(any("Duplicate shard path" in error for error in errors))

    def test_markdown_reports_and_schema_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "a.jsonl"
            second = root / "b.jsonl"
            first.write_text("a\n", encoding="utf-8")
            second.write_text("b\n", encoding="utf-8")
            baseline = build_manifest([first])
            candidate = build_manifest([first, second])
            plan = build_worker_plan(candidate.records, seed=1, worker_count=1, worker_id=0)

            summary = manifest_summary_markdown(candidate)
            diff = diff_to_markdown(baseline, candidate)
            plan_report = worker_plan_markdown(plan)
            schema = manifest_schema_markdown()

        self.assertIn("ShardFlow Manifest Summary", summary)
        self.assertIn("Added", diff)
        self.assertIn("ShardFlow Worker Plan", plan_report)
        self.assertIn("shardflow.manifest.v1", schema)

    def test_cli_helpers_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            shard = root / "shard.jsonl"
            manifest_path = root / "manifest.json"
            checkpoint_path = root / "checkpoint.json"
            shard.write_text('{"text":"hello"}\n', encoding="utf-8")

            self.assertEqual(run(["index", str(root), "--output", str(manifest_path)]), 0)
            self.assertEqual(
                run(["inspect", "--manifest", str(manifest_path), "--format", "json"]),
                0,
            )
            self.assertEqual(run(["schema", "--format", "json"]), 0)
            self.assertEqual(
                run(
                    [
                        "plan",
                        "--manifest",
                        str(manifest_path),
                        "--seed",
                        "7",
                        "--worker-count",
                        "2",
                        "--all-workers",
                    ]
                ),
                0,
            )
            self.assertEqual(
                run(
                    [
                        "checkpoint",
                        "--manifest",
                        str(manifest_path),
                        "--checkpoint",
                        str(checkpoint_path),
                        "--format",
                        "markdown",
                    ]
                ),
                0,
            )
            self.assertEqual(
                run(["doctor", "--data-dir", str(root), "--format", "json"]),
                0,
            )


if __name__ == "__main__":
    unittest.main()
