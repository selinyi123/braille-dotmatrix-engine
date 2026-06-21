from __future__ import annotations
import argparse, json
from pathlib import Path
from .engine import BrailleArtConfig, create_demo_image, process_image
from .benchmark import run_benchmark_suite, write_benchmark_csv
from .brf import attach_brf_artifact_to_report, write_brf_text
from .embosser import GenericEmbosserProfile


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError('value must be a positive integer')
    return parsed


def _unit_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0 or parsed > 1:
        raise argparse.ArgumentTypeError('value must be between 0 and 1')
    return parsed


def _write_report_json(report: dict, report_json: str) -> None:
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Unicode Braille and ASCII visual-symbol renderer")
    p.add_argument("image", nargs="?")
    p.add_argument("--width-cells", type=_positive_int, default=80)
    p.add_argument("--mode", choices=["TACTILE", "SCREEN", "CHROMATIC", "ASCII_MONO", "ASCII_COLOR"], default="TACTILE")
    p.add_argument("--output-png", default="output_braille.png")
    p.add_argument("--output-txt", default="output_braille.txt")
    p.add_argument("--report-json", default="render_report.json")
    p.add_argument("--output-svg", default=None)
    p.add_argument("--output-html", default=None)
    p.add_argument("--output-brf", default=None, help="optional six-dot Braille ASCII / BRF-like text artifact path")
    p.add_argument("--brf-cols", type=_positive_int, default=None, help="optional BRF cells per line override")
    p.add_argument("--brf-rows", type=_positive_int, default=None, help="optional BRF lines per page override")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-invert", action="store_true")
    p.add_argument("--strict-tactile", action="store_true", help="fail tactile-mode export when tactile validation reports errors")
    p.add_argument("--ascii-charset", default=None)
    p.add_argument("--ascii-preset", choices=["custom", "standard", "dense", "blocks", "binary"], default=None)
    p.add_argument("--ascii-aspect", type=float, default=None)
    p.add_argument("--ascii-edge-weight", type=float, default=None)
    p.add_argument("--ascii-html", action="store_true")
    p.add_argument("--braille-target-density", type=_unit_float, default=None)
    p.add_argument("--benchmark", action="store_true", help="run the benchmark suite instead of rendering one image")
    p.add_argument("--benchmark-csv", default="benchmark.csv")
    a = p.parse_args(argv)
    if a.benchmark:
        rows = run_benchmark_suite(output_dir=Path(a.benchmark_csv).parent or Path('.'))
        write_benchmark_csv(rows, a.benchmark_csv)
        print(json.dumps({'benchmark_csv': a.benchmark_csv, 'rows': rows}, indent=2, ensure_ascii=False))
        return 0
    for target in [a.output_png, a.output_txt, a.report_json, a.output_svg, a.output_html, a.output_brf]:
        if target is not None:
            Path(target).parent.mkdir(parents=True, exist_ok=True)
    image = a.image or create_demo_image("test_input.png")
    cfg = BrailleArtConfig(
        output_width_cells=a.width_cells,
        mode=a.mode,
        seed=a.seed,
        invert_luminance=not a.no_invert,
        strict_tactile_validation=bool(a.strict_tactile),
    )
    if a.ascii_charset is not None:
        cfg.ascii_charset = a.ascii_charset
        cfg.ascii_charset_preset = 'custom'
    if a.ascii_preset is not None:
        cfg.ascii_charset_preset = a.ascii_preset
    if a.ascii_aspect is not None:
        cfg.ascii_aspect_ratio = a.ascii_aspect
    if a.ascii_edge_weight is not None:
        cfg.ascii_edge_weight = a.ascii_edge_weight
    if a.ascii_html:
        cfg.ascii_html = True
    if a.braille_target_density is not None:
        cfg.braille_target_density = a.braille_target_density
    report = process_image(image, cfg, a.output_png, a.output_txt, a.report_json, a.output_svg, a.output_html)
    if a.output_brf is not None:
        profile = GenericEmbosserProfile(max_cols=a.brf_cols, max_rows=a.brf_rows)
        source_text = Path(a.output_txt).read_text(encoding='utf-8')
        brf_report = write_brf_text(source_text, a.output_brf, profile)
        report = attach_brf_artifact_to_report(
            report,
            output_brf=a.output_brf,
            output_png=a.output_png,
            output_txt=a.output_txt,
            report_json=a.report_json,
            output_svg=a.output_svg,
            output_html=a.output_html,
            brf_report=brf_report,
        )
        _write_report_json(report, a.report_json)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
