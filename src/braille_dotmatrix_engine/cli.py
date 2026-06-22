from __future__ import annotations
import argparse, json
from pathlib import Path
from .engine import BrailleArtConfig, create_demo_image, process_image
from .benchmark import run_benchmark_suite, write_benchmark_csv
from .brf import BrfExportError, attach_brf_artifact_to_report, validate_brf_text, write_brf_text
from .brf_batch import resolve_brf_input_paths, validate_brf_files
from .embosser import build_embosser_profile, embosser_profile_names
from .schema import PACKAGE_VERSION, RENDER_SCHEMA_VERSION

BRF_COMPATIBLE_MODES = {"TACTILE", "SCREEN", "CHROMATIC"}


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
    Path(report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _validate_brf_mode(parser: argparse.ArgumentParser, mode: str, output_brf: str | None, validate_only: bool) -> None:
    if (output_brf is not None or validate_only) and mode not in BRF_COMPATIBLE_MODES:
        allowed = ', '.join(sorted(BRF_COMPATIBLE_MODES))
        parser.error(f'BRF output requires a Braille-backed mode: {allowed}')


def _base_preflight_report(mode: str, strategy: str, reason: str) -> dict:
    return {
        'package_version': PACKAGE_VERSION,
        'schema_version': RENDER_SCHEMA_VERSION,
        'mode': mode,
        'renderer': {'strategy': strategy, 'backend': 'BRF_TEXT', 'braille_pipeline_executed': False},
        'diagnostics': {'braille_pipeline': {'executed': False, 'reason': reason}},
    }


def _run_brf_preflight(args) -> int:
    source_path = Path(args.brf_preflight)
    profile = build_embosser_profile(args.brf_profile, max_cols=args.brf_cols, max_rows=args.brf_rows)
    brf_report = validate_brf_text(source_path.read_text(encoding='utf-8'), profile, strict=bool(args.strict_brf))
    report = _base_preflight_report('BRF_PREFLIGHT', 'BrfPreflight', 'text-only BRF preflight')
    report = attach_brf_artifact_to_report(report, output_brf=None, output_png=None, output_txt=source_path, report_json=args.report_json, output_svg=None, output_html=None, brf_report=brf_report)
    _write_report_json(report, args.report_json)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.brf_print_summary:
        print(brf_report['summary'])
    return 2 if args.strict_brf and brf_report['diagnostics']['total'] > 0 else 0


def _run_brf_preflight_batch(args) -> int:
    profile = build_embosser_profile(args.brf_profile, max_cols=args.brf_cols, max_rows=args.brf_rows)
    paths = resolve_brf_input_paths(args.brf_preflight_batch, args.brf_batch_pattern)
    batch = validate_brf_files(paths, profile, strict=bool(args.strict_brf))
    report = _base_preflight_report('BRF_PREFLIGHT_BATCH', 'BrfPreflightBatch', 'batch text-only BRF preflight')
    report['batch'] = {'root': str(args.brf_preflight_batch), 'pattern': args.brf_batch_pattern, **batch}
    _write_report_json(report, args.report_json)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.brf_print_summary:
        agg = report['batch']['aggregate']
        print(f"BRF batch; files={agg['total_files']}; ok={agg['ok_files']}; warnings={agg['warning_count']}; errors={agg['error_count']}; issue_files={agg['issue_files']}")
    return 2 if args.strict_brf and report['batch']['aggregate']['issue_files'] > 0 else 0


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
    p.add_argument("--output-brf", default=None, help="optional six-dot Braille ASCII / BRF-like text artifact path; requires TACTILE, SCREEN, or CHROMATIC mode")
    p.add_argument("--brf-profile", choices=embosser_profile_names(), default="a4-40x25", help="named BRF embosser profile preset")
    p.add_argument("--brf-cols", type=_positive_int, default=None, help="optional BRF cells per line override")
    p.add_argument("--brf-rows", type=_positive_int, default=None, help="optional BRF lines per page override")
    p.add_argument("--strict-brf", action="store_true", help="validate BRF diagnostics")
    p.add_argument("--brf-validate-only", action="store_true", help="add BRF diagnostics to the report without writing a BRF file")
    p.add_argument("--brf-preflight", default=None, help="validate an existing Unicode Braille text file without rendering an image")
    p.add_argument("--brf-preflight-batch", default=None, help="validate a file or directory of Unicode Braille text files")
    p.add_argument("--brf-batch-pattern", default="*.txt", help="glob pattern for directory batch preflight")
    p.add_argument("--brf-print-summary", action="store_true", help="print a compact BRF summary line after JSON output")
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
    if a.brf_preflight is not None:
        return _run_brf_preflight(a)
    if a.brf_preflight_batch is not None:
        return _run_brf_preflight_batch(a)
    _validate_brf_mode(p, a.mode, a.output_brf, bool(a.brf_validate_only))
    for target in [a.output_png, a.output_txt, a.report_json, a.output_svg, a.output_html, a.output_brf]:
        if target is not None:
            Path(target).parent.mkdir(parents=True, exist_ok=True)
    image = a.image or create_demo_image("test_input.png")
    cfg = BrailleArtConfig(output_width_cells=a.width_cells, mode=a.mode, seed=a.seed, invert_luminance=not a.no_invert, strict_tactile_validation=bool(a.strict_tactile))
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
    if a.output_brf is not None or a.brf_validate_only:
        profile = build_embosser_profile(a.brf_profile, max_cols=a.brf_cols, max_rows=a.brf_rows)
        source_text = Path(a.output_txt).read_text(encoding='utf-8')
        exit_code = 0
        if a.brf_validate_only:
            brf_report = validate_brf_text(source_text, profile, strict=bool(a.strict_brf))
            if a.strict_brf and brf_report['diagnostics']['total'] > 0:
                exit_code = 2
        else:
            try:
                brf_report = write_brf_text(source_text, a.output_brf, profile, strict=bool(a.strict_brf))
            except BrfExportError as exc:
                brf_report = dict(exc.report)
                brf_report['path'] = str(a.output_brf)
                brf_report['bytes'] = 0
                brf_report['validate_only'] = False
                exit_code = 2
        report = attach_brf_artifact_to_report(report, output_brf=None if a.brf_validate_only else a.output_brf, output_png=a.output_png, output_txt=a.output_txt, report_json=a.report_json, output_svg=a.output_svg, output_html=a.output_html, brf_report=brf_report)
        _write_report_json(report, a.report_json)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if a.brf_print_summary:
            print(brf_report['summary'])
        return exit_code
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
