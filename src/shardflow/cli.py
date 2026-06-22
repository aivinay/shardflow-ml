from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .checkpoint import Checkpoint
from .doctor import diagnostics_to_json, diagnostics_to_markdown, run_diagnostics
from .index import build_manifest
from .manifest import (
    load_manifest,
    remaining_records,
    save_manifest,
    validate_manifest,
    verify_manifest,
)
from .planner import build_worker_plan, plan_all_workers
from .reports import (
    all_worker_plans_json,
    diff_to_json,
    diff_to_markdown,
    manifest_schema_json,
    manifest_schema_markdown,
    manifest_summary_json,
    manifest_summary_markdown,
    worker_plan_json,
    worker_plan_markdown,
)


def main() -> None:
    raise SystemExit(run())


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="shardflow")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index = subparsers.add_parser(
        "index",
        help="Build a manifest for local shard files or directories.",
    )
    index.add_argument("paths", nargs="+", type=Path)
    index.add_argument("--output", "-o", type=Path)

    plan = subparsers.add_parser("plan", help="Create a deterministic worker plan from a manifest.")
    plan.add_argument("--manifest", required=True, type=Path)
    plan.add_argument("--seed", required=True, type=int)
    plan.add_argument("--worker-count", type=int, default=1)
    plan.add_argument("--worker-id", type=int, default=0)
    plan.add_argument(
        "--checkpoint",
        type=Path,
        help="Optional checkpoint; processed shards are excluded from the plan.",
    )
    plan.add_argument("--all-workers", action="store_true", help="Emit plans for every worker.")
    plan.add_argument("--format", choices=["json", "markdown"], default="json")
    plan.add_argument("--output", "-o", type=Path)

    checkpoint = subparsers.add_parser("checkpoint", help="Summarize checkpoint progress.")
    checkpoint.add_argument("--manifest", required=True, type=Path)
    checkpoint.add_argument("--checkpoint", required=True, type=Path)
    checkpoint.add_argument("--format", choices=["json", "markdown"], default="json")

    verify = subparsers.add_parser(
        "verify",
        help="Verify manifest files, sizes, and checksums against disk.",
    )
    verify.add_argument("--manifest", required=True, type=Path)

    diff = subparsers.add_parser("diff", help="Compare two manifests by path, size, and checksum.")
    diff.add_argument("baseline", type=Path)
    diff.add_argument("candidate", type=Path)
    diff.add_argument("--format", choices=["json", "markdown"], default="json")

    inspect = subparsers.add_parser("inspect", help="Summarize a manifest.")
    inspect.add_argument("--manifest", required=True, type=Path)
    inspect.add_argument("--format", choices=["json", "markdown"], default="json")

    schema = subparsers.add_parser("schema", help="Print the manifest schema.")
    schema.add_argument("--format", choices=["json", "markdown"], default="markdown")

    doctor = subparsers.add_parser(
        "doctor",
        help="Check local installation and optional data input.",
    )
    doctor.add_argument(
        "--data-dir",
        type=Path,
        help="Optional data directory to index and verify.",
    )
    doctor.add_argument("--format", choices=["json", "markdown"], default="markdown")

    args = parser.parse_args(argv)
    if args.command == "index":
        manifest = build_manifest(args.paths)
        errors = validate_manifest(manifest)
        if errors:
            raise ValueError("; ".join(errors))
        payload = json.dumps(manifest.to_dict(), indent=2, sort_keys=True)
        if args.output:
            save_manifest(manifest, args.output)
        else:
            print(payload)
    elif args.command == "plan":
        manifest = load_manifest(args.manifest)
        records = manifest.records
        if args.checkpoint:
            state = Checkpoint.load(args.checkpoint) if args.checkpoint.exists() else Checkpoint()
            records = remaining_records(manifest, state)
        if args.all_workers:
            plans = plan_all_workers(records, seed=args.seed, worker_count=args.worker_count)
            if args.format == "markdown":
                payload = "\n".join(worker_plan_markdown(plan) for plan in plans.values())
            else:
                payload = all_worker_plans_json(plans)
        else:
            plan_payload = build_worker_plan(
                records,
                seed=args.seed,
                worker_count=args.worker_count,
                worker_id=args.worker_id,
            )
            payload = (
                worker_plan_markdown(plan_payload)
                if args.format == "markdown"
                else worker_plan_json(plan_payload)
            )
        if args.output:
            args.output.write_text(payload.rstrip() + "\n", encoding="utf-8")
        else:
            print(payload)
    elif args.command == "checkpoint":
        manifest = load_manifest(args.manifest)
        state = Checkpoint.load(args.checkpoint) if args.checkpoint.exists() else Checkpoint()
        summary = state.summary(manifest.shard_ids())
        if args.format == "markdown":
            print(_checkpoint_markdown(summary), end="")
        else:
            print(json.dumps(summary, indent=2, sort_keys=True))
    elif args.command == "verify":
        errors = verify_manifest(load_manifest(args.manifest))
        print(json.dumps({"passed": not errors, "errors": errors}, indent=2, sort_keys=True))
        if errors:
            return 2
    elif args.command == "diff":
        baseline = load_manifest(args.baseline)
        candidate = load_manifest(args.candidate)
        if args.format == "markdown":
            print(diff_to_markdown(baseline, candidate), end="")
        else:
            print(diff_to_json(baseline, candidate))
    elif args.command == "inspect":
        manifest = load_manifest(args.manifest)
        if args.format == "markdown":
            print(manifest_summary_markdown(manifest), end="")
        else:
            print(manifest_summary_json(manifest))
    elif args.command == "schema":
        if args.format == "json":
            print(manifest_schema_json())
        else:
            print(manifest_schema_markdown(), end="")
    elif args.command == "doctor":
        checks = run_diagnostics(args.data_dir)
        if args.format == "json":
            print(diagnostics_to_json(checks))
        else:
            print(diagnostics_to_markdown(checks), end="")
        if not all(check.passed for check in checks):
            return 1
    return 0


def _checkpoint_markdown(summary: dict[str, int]) -> str:
    return "\n".join(
        [
            "# ShardFlow Checkpoint Summary",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Total | {summary['total']} |",
            f"| Processed | {summary['processed']} |",
            f"| Failed | {summary['failed']} |",
            f"| Remaining | {summary['remaining']} |",
            "",
        ]
    )


if __name__ == "__main__":
    main()
