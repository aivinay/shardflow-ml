from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .index import build_manifest
from .manifest import validate_manifest, verify_manifest


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
        }


def run_diagnostics(data_dir: Path | None = None) -> list[DoctorCheck]:
    checks = [_check_sha256()]
    if data_dir is not None:
        checks.append(_check_manifest_roundtrip(data_dir))
    return checks


def diagnostics_to_json(checks: list[DoctorCheck]) -> str:
    payload = {
        "passed": all(check.passed for check in checks),
        "checks": [check.to_dict() for check in checks],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def diagnostics_to_markdown(checks: list[DoctorCheck]) -> str:
    lines = [
        "# ShardFlow Doctor",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        status = "pass" if check.passed else "fail"
        lines.append(f"| {check.name} | {status} | {check.detail} |")
    return "\n".join(lines) + "\n"


def _check_sha256() -> DoctorCheck:
    digest = hashlib.sha256(b"shardflow").hexdigest()
    if len(digest) != 64:
        return DoctorCheck("sha256", False, "unexpected digest length")
    return DoctorCheck("sha256", True, "SHA-256 hashing is available")


def _check_manifest_roundtrip(data_dir: Path) -> DoctorCheck:
    try:
        manifest = build_manifest([data_dir])
        errors = validate_manifest(manifest) + verify_manifest(manifest)
    except Exception as exc:
        return DoctorCheck("manifest", False, str(exc))
    if errors:
        return DoctorCheck("manifest", False, "; ".join(errors))
    return DoctorCheck("manifest", True, f"{len(manifest.records)} shards indexed and verified")
