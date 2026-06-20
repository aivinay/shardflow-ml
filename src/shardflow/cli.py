from __future__ import annotations

import argparse
import json
from pathlib import Path

from .index import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(prog="shardflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index = subparsers.add_parser("index", help="Build a manifest for local shard files.")
    index.add_argument("paths", nargs="+", type=Path)

    args = parser.parse_args()
    if args.command == "index":
        manifest = build_manifest(args.paths)
        print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
