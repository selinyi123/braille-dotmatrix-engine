from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .report_diff import diff_reports
from .report_diff_policy import evaluate_report_diff_policy


@dataclass
class MigrationPlan:
    should_migrate: bool
    drift_count: int
    summary: str


def build_migration_plan(old_contract: dict[str, Any], new_contract: dict[str, Any]) -> MigrationPlan:
    diff = diff_reports(old_contract, new_contract)
    policy = evaluate_report_diff_policy(diff)

    return MigrationPlan(
        should_migrate=policy["status"] == "fail",
        drift_count=policy["drift_count"],
        summary=policy.get("summary", ""),
    )


def write_migration_plan(plan: MigrationPlan, output: str | Path) -> None:
    data = {
        "should_migrate": plan.should_migrate,
        "drift_count": plan.drift_count,
        "summary": plan.summary,
    }
    Path(output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Contract migration planner")
    parser.add_argument("old", help="old contract json")
    parser.add_argument("new", help="new contract json")
    parser.add_argument("--output", required=False)
    args = parser.parse_args(argv)

    old = json.loads(Path(args.old).read_text(encoding="utf-8"))
    new = json.loads(Path(args.new).read_text(encoding="utf-8"))

    plan = build_migration_plan(old, new)

    if args.output:
        write_migration_plan(plan, args.output)

    print(json.dumps(plan.__dict__, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())