from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .json_utils import dumps_json, write_json

REPORT_DIFF_POLICY_SCHEMA_VERSION = "1.0"

__all__ = ["REPORT_DIFF_POLICY_SCHEMA_VERSION", "evaluate_report_diff_policy", "write_report_diff_policy"]


def evaluate_report_diff_policy(diff: dict[str, Any], *, policy: str = "blocking") -> dict[str, Any]:
    counts = diff.get("counts")
    if not isinstance(counts, dict) or "total" not in counts:
        raise ValueError("expected report diff with counts.total")
    drift_count = int(counts["total"])
    status = "pass" if drift_count == 0 else "fail"
    return {
        "schema": "braille-dotmatrix-engine.report_diff_policy",
        "schema_version": REPORT_DIFF_POLICY_SCHEMA_VERSION,
        "policy": policy,
        "status": status,
        "drift_count": drift_count,
        "summary": diff.get("summary", ""),
        "counts": counts,
    }


def write_report_diff_policy(diff_path: str | Path, output_path: str | Path, *, policy: str = "blocking") -> dict[str, Any]:
    diff = json.loads(Path(diff_path).read_text(encoding="utf-8"))
    result = evaluate_report_diff_policy(diff, policy=policy)
    write_json(result, output_path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a report diff against a CI drift policy")
    parser.add_argument("diff", help="report diff JSON path")
    parser.add_argument("--output", default=None, help="optional policy JSON output path")
    parser.add_argument("--policy", default="blocking", help="policy label recorded in the output JSON")
    parser.add_argument("--enforce", action="store_true", help="return non-zero when drift_count is greater than zero")
    args = parser.parse_args(argv)
    diff = json.loads(Path(args.diff).read_text(encoding="utf-8"))
    result = evaluate_report_diff_policy(diff, policy=args.policy)
    if args.output is not None:
        write_json(result, args.output)
    print(dumps_json(result))
    if args.enforce and result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
