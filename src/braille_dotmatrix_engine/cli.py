from __future__ import annotations
import argparse, json
from .engine import BrailleArtConfig, create_demo_image, process_image

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Unicode Braille dot-matrix art renderer")
    p.add_argument("image", nargs="?")
    p.add_argument("--width-cells", type=int, default=80)
    p.add_argument("--mode", choices=["TACTILE", "SCREEN"], default="TACTILE")
    p.add_argument("--output-png", default="output_braille.png")
    p.add_argument("--output-txt", default="output_braille.txt")
    p.add_argument("--report-json", default="render_report.json")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-invert", action="store_true")
    a = p.parse_args(argv)
    image = a.image or create_demo_image("test_input.png")
    cfg = BrailleArtConfig(output_width_cells=a.width_cells, mode=a.mode, seed=a.seed, invert_luminance=not a.no_invert)
    report = process_image(image, cfg, a.output_png, a.output_txt, a.report_json)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
