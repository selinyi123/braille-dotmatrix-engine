# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, terminal text art, HTML previews, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSVs.

## Current version

`v1.9.0`

## Status

This repository is currently in the **V1 engineering prototype** stage:

- Unicode Braille encoding and decoding
- image-to-dot sampling
- CLAHE preprocessing
- edge-aware Braille sampling enhancement
- Braille density target control and seam diagnostics
- serpentine error-diffusion dithering
- tactile, screen, `CHROMATIC`, `ASCII_MONO`, and `ASCII_COLOR` rendering modes
- ASCII charset presets and optional HTML export
- PNG, TXT, JSON report, optional SVG/HTML export, and benchmark CSV output
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

The next major direction is **Semantic Braille Engine**: image regions should be weighted by semantic importance before tactile/Braille export.

## Install

```bash
pip install -e ".[dev]"
```

## CLI usage

Generate a demo image and render it:

```bash
braille-dotmatrix --width-cells 80
```

Render an input image in tactile mode:

```bash
braille-dotmatrix input.png \
  --width-cells 100 \
  --mode TACTILE \
  --braille-target-density 0.38 \
  --output-png artifacts/output_braille.png \
  --output-txt artifacts/output_braille.txt \
  --report-json artifacts/render_report.json \
  --output-svg artifacts/output_braille.svg
```

Render ASCII art:

```bash
braille-dotmatrix input.png \
  --width-cells 120 \
  --mode ASCII_MONO \
  --ascii-preset dense \
  --output-png artifacts/ascii_preview.png \
  --output-txt artifacts/ascii.txt \
  --report-json artifacts/ascii_report.json
```

Render ANSI color ASCII art with HTML preview:

```bash
braille-dotmatrix input.png \
  --width-cells 120 \
  --mode ASCII_COLOR \
  --ascii-preset blocks \
  --ascii-html \
  --output-txt artifacts/ascii_color.ansi \
  --output-html artifacts/ascii_color.html \
  --report-json artifacts/ascii_color_report.json
```

Render a colored dot-matrix screen preview:

```bash
braille-dotmatrix input.png \
  --width-cells 100 \
  --mode CHROMATIC \
  --output-png artifacts/chromatic.png \
  --output-txt artifacts/chromatic.txt \
  --report-json artifacts/chromatic_report.json
```

Strict tactile validation mode:

```bash
braille-dotmatrix input.png --mode TACTILE --strict-tactile
```

Run smoke benchmarks:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

## Python API

```python
from braille_dotmatrix_engine import BrailleArtConfig, process_image

cfg = BrailleArtConfig(
    output_width_cells=100,
    mode="ASCII_MONO",
    ascii_charset_preset="dense",
    braille_target_density=0.38,
    seed=42,
)

report = process_image(
    "input.png",
    cfg,
    output_png="artifacts/output.png",
    output_txt="artifacts/output.txt",
    report_json="artifacts/render_report.json",
    output_html="artifacts/output.html",
)
```

## Unicode Braille mapping

The engine uses the official physical 8-dot Braille layout:

```text
1 4
2 5
3 6
7 8
```

Mapped to Unicode bit positions:

```text
bit0 bit3
bit1 bit4
bit2 bit5
bit6 bit7
```

This means every 4x2 physical dot block can be encoded into one Unicode Braille character.

## Outputs

| Output | Purpose |
|---|---|
| `.png` | tactile black/white raster, monochrome screen preview, chromatic preview, or ASCII preview artifact |
| `.txt` | copyable Unicode Braille or ASCII art text |
| `.ansi` | ANSI-colored ASCII text |
| `.html` | browser-previewable ASCII art using monospace layout |
| `.json` | render report, metrics, validation status, config, Braille/ASCII quality diagnostics |
| `.svg` | physical millimeter-space tactile vector export |
| `.csv` | benchmark runtime / memory / quality table |

## Validation and quality layer

Current validation and quality reporting includes:

- exhaustive 256-pattern Unicode roundtrip
- physical spacing and safety-gap report
- active-dot collision report
- raster roundtrip check for tactile PNG mode
- occupancy and local-density metrics
- Braille density target control
- Braille tile seam diagnostics
- ASCII tone score, edge score, charset preset, and HTML availability
- deterministic density correction using `np.random.default_rng(seed)`

## Design direction

The project should not remain only a Braille-art converter. The intended evolution is:

```text
V1 Braille + ASCII Multi-Symbol Renderer
↓
V2 Semantic Braille Engine
↓
V3 Tactile Graphics Pipeline
↓
V4 Visual Semantic Encoding Layer
```

See [`ROADMAP.md`](ROADMAP.md), [`docs/ROADMAP_V2.md`](docs/ROADMAP_V2.md), and [`docs/PROJECT_DESIGN.md`](docs/PROJECT_DESIGN.md).

## Tests

```bash
pytest -q
```

## License

MIT
