import tempfile
import unittest
from pathlib import Path

from shardflow import Checkpoint, build_manifest, plan_epoch


class ShardFlowTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_checksummed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            second = root / "b.jsonl"
            first = root / "a.jsonl"
            second.write_text("second\n", encoding="utf-8")
            first.write_text("first\n", encoding="utf-8")

            manifest = build_manifest([second, first])

            self.assertEqual([Path(record.path).name for record in manifest.records], ["a.jsonl", "b.jsonl"])
            self.assertEqual(manifest.to_dict()["shard_count"], 2)
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

    def test_checkpoint_roundtrip_tracks_remaining_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            checkpoint = Checkpoint()
            checkpoint.mark_processed("shard-a")
            checkpoint.mark_failed("shard-b", "decode error")
            checkpoint.save(path)

            loaded = Checkpoint.load(path)

            self.assertEqual(loaded.remaining(["shard-a", "shard-b", "shard-c"]), ["shard-b", "shard-c"])
            self.assertEqual(loaded.failed, {"shard-b": "decode error"})


if __name__ == "__main__":
    unittest.main()
