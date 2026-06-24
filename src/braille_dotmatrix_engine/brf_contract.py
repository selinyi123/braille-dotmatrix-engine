from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .json_utils import dumps_json, write_json

__all__ = ["batch_contract_from_report", "write_batch_contract_from_report"]

AGGREGATE_CONTRACT_KEYS = (
    "total_files",
    "ok_files",
    "warning_files",
    "error_files",
    "issue_files",
    "warning_count",
    "error_count",
    "by_reason",
)


def _file_name(item: dict[str, Any]) -> str:
    if "name" in item:
        return str(item["name"])
    if "path" in item:
        return Path(str(item["path"])).name
    return ""


def _aggregate_contract(aggregate: dict[str, Any]) -> dict[str, Any]:
    return {key: aggregate[key] for key in AGGREGATE_CONTRACT_KEYS}


def batch_contract_from_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return the stable BRF batch contract shape used by checked-in JSON fixtures."""
    batch = report.get("batch", report)
    if "aggregate" not in batch or "files" not in batch:
        raise ValueError("expected BRF batch report or contract with aggregate and files fields")
    return {
        "aggregate": _aggregate_contract(batch["aggregate"]),
        "files": [
            {
                "name": _file_name(item),
                "summary": item["summary"],
                "ok": item["ok"],
                "warning_count": item["warning_count"],
                "error_count": item["error_count"],
            }
            for item in batch["files"]
        ],
    }


def write_batch_contract_from_report(report_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    contract = batch_contract_from_report(report)
    write_json(contract, output_path)
    return contract


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize a BRF batch report into the checked-in contract shape")
    parser.add_argument("report", help="BRF batch report JSON path")
    parser.add_argument("--output", required=True, help="contract JSON output path")
    args = parser.parse_args(argv)
    contract = write_batch_contract_from_report(args.report, args.output)
    print(dumps_json(contract))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
