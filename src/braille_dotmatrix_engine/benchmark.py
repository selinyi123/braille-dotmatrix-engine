from __future__ import annotations

import argparse
import csv
import math
import time
from pathlib import Path

try:  # Windows does not provide the POSIX resource module.
    import resource
except ImportError:  # pragma: no cover - exercised on Windows.
    resource = None

import cv2
import numpy as np

from .config import BrailleArtConfig
from .json_utils import dumps_json, write_json
from .pipeline import process_image
from .runtime_validation import require_finite
from .schema import BENCHMARK_SCHEMA_VERSION, RENDER_SCHEMA_VERSION

BENCHMARK_PROFILES: dict[str, list[tuple[str, tuple[int, int]]]] = {
    "smoke": [
        ("smoke_128", (96, 128)),
        ("smoke_256", (192, 256)),
    ],
    "medium": [
        ("medium_720p", (720, 1280)),
        ("medium_1080p", (1080, 1920)),
    ],
    "stress": [
        ("stress_4k", (2160, 3840)),
    ],
}

__all__ = [
    "BENCHMARK_PROFILES",
    "BENCHMARK_SCHEMA_VERSION",
    "create_synthetic_image",
    "estimate_image_memory_mb",
    "run_one_benchmark",
    "run_benchmark_suite",
    "validate_benchmark_rows",
    "write_benchmark_csv",
    "write_benchmark_summary",
    "main",
]


def _rss_mb() -> float:
    if resource is None:
        return 0.0
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB, macOS reports bytes. GitHub Actions is Linux, but keep
    # the fallback safe for local usage.
    if usage > 10_000_000:
        return float(usage / (1024 * 1024))
    return float(usage / 1024)


def _finite_float(value, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def _positive_finite_float(value: str) -> float:
    try:
        parsed = require_finite('value', value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None
    if parsed <= 0:
        raise argparse.ArgumentTypeError('value must be positive')
    return parsed


def _file_size_bytes(path) -> int:
    if path is None:
        return 0
    candidate = Path(path)
    return candidate.stat().st_size if candidate.exists() else 0


def estimate_image_memory_mb(width: int, height: int) -> dict[str, float]:
    pixels = max(0, int(width)) * max(0, int(height))
    mib = 1024 * 1024
    input_rgb = pixels * 3
    gray_float = pixels * 4
    lab_or_enhanced = pixels * 3
    scratch = pixels * 4
    estimated_working_set = input_rgb + gray_float + lab_or_enhanced + scratch
    return {
        "input_image_mb": round(input_rgb / mib, 3),
        "estimated_working_set_mb": round(estimated_working_set / mib, 3),
    }


def create_synthetic_image(path, width: int = 256, height: int = 192) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.linspace(0, 1, width, dtype=np.float32)
    y = np.linspace(0, 1, height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    r = np.clip(255 * xx, 0, 255)
    g = np.clip(255 * yy, 0, 255)
    b = np.clip(255 * (0.55 + 0.45 * np.sin(8 * xx) * np.cos(6 * yy)), 0, 255)
    img = np.stack([b, g, r], axis=-1).astype(np.uint8)
    cv2.circle(img, (width // 2, height // 2), max(8, min(width, height) // 5), (245, 245, 245), -1)
    cv2.line(img, (0, height - 1), (width - 1, 0), (20, 20, 20), 3)
    cv2.imwrite(str(path), img)
    return str(path)


def run_one_benchmark(name: str, image_shape: tuple[int, int], mode: str, output_dir="artifacts/benchmarks", profile: str = "custom") -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    height, width = image_shape
    image = create_synthetic_image(output_dir / f"{name}_{mode.lower()}_input.png", width=width, height=height)
    cfg = BrailleArtConfig(output_width_cells=max(12, min(96, width // 8)), mode=mode, render_spacing_px=6)
    output_png = output_dir / f"{name}_{mode.lower()}.png"
    output_txt = output_dir / f"{name}_{mode.lower()}.txt"
    report_json = output_dir / f"{name}_{mode.lower()}.json"
    before = _rss_mb()
    start = time.perf_counter()
    report = process_image(
        image,
        cfg,
        output_png,
        output_txt,
        report_json,
    )
    elapsed = time.perf_counter() - start
    after = _rss_mb()
    q = report.get("quality_metrics", {})
    ascii_quality = (report.get("ascii_render") or {}).get("quality", {})
    memory_estimate = estimate_image_memory_mb(width, height)
    artifact_png_bytes = _file_size_bytes(output_png)
    artifact_txt_bytes = _file_size_bytes(output_txt)
    artifact_report_bytes = _file_size_bytes(report_json)
    artifact_input_bytes = _file_size_bytes(image)
    return {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "name": name,
        "profile": profile,
        "mode": mode,
        "width": width,
        "height": height,
        "input_pixels": int(width * height),
        "input_megapixels": round((width * height) / 1_000_000, 6),
        "runtime_sec": round(_finite_float(elapsed), 6),
        "rss_delta_mb": round(float(max(0.0, after - before)), 3),
        "rss_peak_mb": round(_finite_float(after), 3),
        "estimated_input_mb": memory_estimate["input_image_mb"],
        "estimated_working_set_mb": memory_estimate["estimated_working_set_mb"],
        "artifact_input_bytes": artifact_input_bytes,
        "artifact_png_bytes": artifact_png_bytes,
        "artifact_txt_bytes": artifact_txt_bytes,
        "artifact_report_bytes": artifact_report_bytes,
        "artifact_total_bytes": artifact_input_bytes + artifact_png_bytes + artifact_txt_bytes + artifact_report_bytes,
        "occupancy_ratio": round(_finite_float(report.get("occupancy_ratio")), 6),
        "tone_psnr": round(_finite_float(q.get("psnr", q.get("tone_psnr", 0.0))), 6),
        "tone_score": round(_finite_float(ascii_quality.get("tone_score", 0.0)), 6),
        "edge_score": round(_finite_float(q.get("edge_score", ascii_quality.get("edge_score", 0.0))), 6),
        "schema_version": report.get("schema_version"),
    }


def run_benchmark_suite(output_dir="artifacts/benchmarks", include_ascii: bool = True, profile: str = "smoke") -> list[dict]:
    if profile not in BENCHMARK_PROFILES:
        raise ValueError(f"unknown benchmark profile: {profile}")
    modes = ["TACTILE", "CHROMATIC"]
    if include_ascii:
        modes.extend(["ASCII_MONO", "ASCII_COLOR"])
    rows: list[dict] = []
    for name, shape in BENCHMARK_PROFILES[profile]:
        for mode in modes:
            rows.append(run_one_benchmark(name, shape, mode, output_dir, profile=profile))
    return rows


def validate_benchmark_rows(rows: list[dict], *, max_runtime_sec: float = 60.0, max_rss_peak_mb: float = 2048.0) -> list[str]:
    issues: list[str] = []
    max_runtime_sec = require_finite('max_runtime_sec', max_runtime_sec)
    max_rss_peak_mb = require_finite('max_rss_peak_mb', max_rss_peak_mb)
    if max_runtime_sec <= 0:
        issues.append('max_runtime_sec must be positive')
    if max_rss_peak_mb <= 0:
        issues.append('max_rss_peak_mb must be positive')
    if not rows:
        return [*issues, "benchmark suite produced no rows"]
    for idx, row in enumerate(rows):
        label = f"row {idx} {row.get('name')} {row.get('mode')}"
        runtime = _finite_float(row.get("runtime_sec"), -1.0)
        rss_peak = _finite_float(row.get("rss_peak_mb"), -1.0)
        occupancy = _finite_float(row.get("occupancy_ratio"), -1.0)
        estimated_working_set = _finite_float(row.get("estimated_working_set_mb"), -1.0)
        artifact_total = int(row.get("artifact_total_bytes") or 0)
        if runtime < 0 or runtime > max_runtime_sec:
            issues.append(f"{label}: runtime_sec {runtime} outside threshold <= {max_runtime_sec}")
        if rss_peak < 0 or rss_peak > max_rss_peak_mb:
            issues.append(f"{label}: rss_peak_mb {rss_peak} outside threshold <= {max_rss_peak_mb}")
        if estimated_working_set < 0:
            issues.append(f"{label}: estimated_working_set_mb {estimated_working_set} must be non-negative")
        if artifact_total < 0:
            issues.append(f"{label}: artifact_total_bytes {artifact_total} must be non-negative")
        if occupancy < 0 or occupancy > 1:
            issues.append(f"{label}: occupancy_ratio {occupancy} outside [0, 1]")
        if row.get("schema_version") != RENDER_SCHEMA_VERSION:
            issues.append(f"{label}: render schema_version is {row.get('schema_version')}, expected {RENDER_SCHEMA_VERSION}")
        if row.get("benchmark_schema_version") != BENCHMARK_SCHEMA_VERSION:
            issues.append(f"{label}: benchmark_schema_version is {row.get('benchmark_schema_version')}, expected {BENCHMARK_SCHEMA_VERSION}")
    return issues


def write_benchmark_csv(rows: list[dict], path="benchmark.csv") -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def write_benchmark_summary(rows: list[dict], path="benchmark_summary.json", *, issues: list[str] | None = None) -> str:
    payload = {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "render_schema_version": RENDER_SCHEMA_VERSION,
        "row_count": len(rows),
        "profiles": sorted({str(row.get("profile")) for row in rows}),
        "modes": sorted({str(row.get("mode")) for row in rows}),
        "max_runtime_sec": max((_finite_float(row.get("runtime_sec")) for row in rows), default=0.0),
        "max_rss_peak_mb": max((_finite_float(row.get("rss_peak_mb")) for row in rows), default=0.0),
        "max_estimated_working_set_mb": max((_finite_float(row.get("estimated_working_set_mb")) for row in rows), default=0.0),
        "total_artifact_bytes": sum(int(row.get("artifact_total_bytes") or 0) for row in rows),
        "issues": issues or [],
        "ok": not issues,
    }
    write_json(payload, path)
    return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Braille Dot-Matrix benchmark suite")
    parser.add_argument("--output-dir", default="artifacts/benchmarks")
    parser.add_argument("--csv", default="artifacts/benchmarks/benchmark.csv")
    parser.add_argument("--summary", default="artifacts/benchmarks/benchmark_summary.json")
    parser.add_argument("--profile", choices=sorted(BENCHMARK_PROFILES), default="smoke")
    parser.add_argument("--max-runtime-sec", type=_positive_finite_float, default=60.0)
    parser.add_argument("--max-rss-mb", type=_positive_finite_float, default=2048.0)
    parser.add_argument("--no-ascii", action="store_true")
    args = parser.parse_args(argv)

    rows = run_benchmark_suite(args.output_dir, include_ascii=not args.no_ascii, profile=args.profile)
    issues = validate_benchmark_rows(rows, max_runtime_sec=args.max_runtime_sec, max_rss_peak_mb=args.max_rss_mb)
    csv_path = write_benchmark_csv(rows, args.csv)
    summary_path = write_benchmark_summary(rows, args.summary, issues=issues)
    print(dumps_json({"csv": csv_path, "summary": summary_path, "issues": issues}))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
