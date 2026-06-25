from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .json_utils import dumps_json, write_json

RELEASE_VERIFICATION_SCHEMA_VERSION = "1.0"
DEFAULT_ONLINE_NOTE = "Requires network access to GitHub and GitHub CLI authentication."
DEFAULT_OFFLINE_NOTE = "Offline verification requires a previously downloaded attestation bundle and trusted certificate material; this helper only records online commands."

__all__ = ["RELEASE_VERIFICATION_SCHEMA_VERSION", "build_release_verification_checklist", "write_release_verification_checklist"]


def _load_plan(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _verify_command(path: str, repository: str) -> str:
    return f"gh attestation verify {path} -R {repository}"


def _artifact_prefix(plan: dict[str, Any], artifact_prefix: str | None) -> str:
    if artifact_prefix is not None:
        return artifact_prefix.rstrip("/")
    artifact_dir = plan.get("artifact_dir")
    if artifact_dir is None:
        return "artifacts/release"
    return str(artifact_dir).rstrip("/")


def build_release_verification_checklist(plan: dict[str, Any], *, repository: str, artifact_prefix: str | None = None) -> dict[str, Any]:
    subjects = plan.get("subjects", [])
    if not isinstance(subjects, list):
        raise ValueError("release attestation plan must contain a subjects list")
    resolved_prefix = _artifact_prefix(plan, artifact_prefix)
    checks = []
    for item in subjects:
        path = str(item["path"])
        artifact_path = f"{resolved_prefix}/{path}"
        checks.append({
            "path": path,
            "artifact_path": artifact_path,
            "sha256": item.get("sha256"),
            "size_bytes": item.get("size_bytes"),
            "command": _verify_command(artifact_path, repository),
        })
    return {
        "schema": "braille-dotmatrix-engine.release_verification",
        "schema_version": RELEASE_VERIFICATION_SCHEMA_VERSION,
        "repository": repository,
        "artifact_prefix": resolved_prefix,
        "subject_count": len(checks),
        "checks": checks,
        "online_verification_note": DEFAULT_ONLINE_NOTE,
        "offline_verification_note": DEFAULT_OFFLINE_NOTE,
        "manual_checklist": [
            "Download the release-artifacts bundle from the release workflow run.",
            "Confirm each artifact hash matches release_attestation_plan.json.",
            "Run each gh attestation verify command listed in this file.",
            "Confirm BRF drift_policy.json reports status=pass.",
            "Archive release_attestation_plan.json and release_verification_checklist.json with the release notes.",
        ],
    }


def write_release_verification_checklist(plan_path: str | Path, output_path: str | Path, *, repository: str, artifact_prefix: str | None = None) -> dict[str, Any]:
    checklist = build_release_verification_checklist(_load_plan(plan_path), repository=repository, artifact_prefix=artifact_prefix)
    write_json(checklist, output_path)
    return checklist


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a release attestation verification checklist from a release attestation plan")
    parser.add_argument("plan", help="release_attestation_plan.json path")
    parser.add_argument("--output", required=True, help="release verification checklist JSON output path")
    parser.add_argument("--repository", required=True, help="owner/repository used by gh attestation verify")
    parser.add_argument("--artifact-prefix", default=None, help="optional path prefix override used in verification commands; defaults to artifact_dir from the plan")
    args = parser.parse_args(argv)
    checklist = write_release_verification_checklist(args.plan, args.output, repository=args.repository, artifact_prefix=args.artifact_prefix)
    print(dumps_json(checklist))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
