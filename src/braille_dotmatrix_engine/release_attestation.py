from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .artifact_provenance import sha256_file
from .json_utils import dumps_json, write_json

RELEASE_ATTESTATION_PLAN_SCHEMA_VERSION = "1.0"

__all__ = ["RELEASE_ATTESTATION_PLAN_SCHEMA_VERSION", "build_release_attestation_plan", "write_release_attestation_plan"]


def _artifact_entry(path: Path, base_dir: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(base_dir).as_posix(),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def build_release_attestation_plan(
    artifact_dir: str | Path,
    *,
    subject_globs: list[str] | None = None,
    workflow: str = "release-attestations",
    trigger_policy: str = "tags-v-and-workflow-dispatch-only",
) -> dict[str, Any]:
    base_dir = Path(artifact_dir)
    patterns = subject_globs or ["*.whl", "*.tar.gz", "brf_batch_report.json", "brf_batch_contract.json", "report_diff.json", "drift_policy.json", "provenance_manifest.json"]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(sorted(path for path in base_dir.glob(pattern) if path.is_file()))
    unique_paths = sorted(set(paths), key=lambda path: path.relative_to(base_dir).as_posix())
    return {
        "schema": "braille-dotmatrix-engine.release_attestation_plan",
        "schema_version": RELEASE_ATTESTATION_PLAN_SCHEMA_VERSION,
        "workflow": workflow,
        "trigger_policy": trigger_policy,
        "artifact_dir": str(base_dir),
        "subject_globs": patterns,
        "subject_count": len(unique_paths),
        "subjects": [_artifact_entry(path, base_dir) for path in unique_paths],
    }


def write_release_attestation_plan(
    artifact_dir: str | Path,
    output_path: str | Path,
    *,
    subject_globs: list[str] | None = None,
    workflow: str = "release-attestations",
    trigger_policy: str = "tags-v-and-workflow-dispatch-only",
) -> dict[str, Any]:
    plan = build_release_attestation_plan(artifact_dir, subject_globs=subject_globs, workflow=workflow, trigger_policy=trigger_policy)
    write_json(plan, output_path)
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a release artifact attestation plan for built release artifacts")
    parser.add_argument("artifact_dir", help="directory containing built release artifacts")
    parser.add_argument("--output", required=True, help="attestation plan JSON output path")
    parser.add_argument("--subject-glob", action="append", default=None, help="artifact glob to include; can be repeated")
    parser.add_argument("--workflow", default="release-attestations", help="workflow label recorded in the plan")
    parser.add_argument("--trigger-policy", default="tags-v-and-workflow-dispatch-only", help="trigger policy label recorded in the plan")
    args = parser.parse_args(argv)
    plan = write_release_attestation_plan(args.artifact_dir, args.output, subject_globs=args.subject_glob, workflow=args.workflow, trigger_policy=args.trigger_policy)
    print(dumps_json(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
