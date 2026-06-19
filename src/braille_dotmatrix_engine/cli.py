from __future__ import annotations
import argparse, json
from pathlib import Path
from .engine import BrailleArtConfig, create_demo_image, process_image


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError('value must be a positive integer')
    return parsed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Unicode Braille dot-matrix art renderer")
    p.add_argument("image", nargs="?")
    p.add_argument("--width-cells", type=_positive_int, default=80)
    p.add_argument("--mode", choices=["TACTILE", "SCREEN"], default="TACTILE")
    p.add_argument("--output-png", default="output_braille.png")
    p.add_argument("--output-txt", default="output_braille.txt")
    p.add_argument("--report-json", default="render_report.json")
    p.add_argument("--output-svg", default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-invert", action="store_true")
    p.add_argument("--strict-tactile", action="store_true", help="fail tactile-mode export when tactile validation reports errors")
    a = p.parse_args(argv)
    for target in [a.output_png, a.output_txt, a.report_json, a.output_svg]:
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
    report = process_image(image, cfg, a.output_png, a.output_txt, a.report_json, a.output_svg)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
