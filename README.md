# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.20.0`

## Status

This repository is currently in the **V1 engineering prototype** stage:

- Unicode Braille encoding and decoding
- image-to-dot sampling
- tactile, screen, `CHROMATIC`, `ASCII_MONO`, and `ASCII_COLOR` rendering modes
- renderer strategy runtime for mode-specific output behavior
- artifact manifest and report adapter layer
- generic embosser export boundary for page/device capacity metadata
- named embosser profile presets for common BRF page capacities
- conservative six-dot BRF-like text export with compatibility diagnostics
- compact BRF report summary and validation-only CLI mode
- text-only BRF preflight mode for existing Unicode Braille TXT files
- benchmark profiles for smoke, medium, and stress image sizes
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- centralized render/benchmark schema constants
- centralized configuration validation before rendering
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.20.0 BRF preflight input notes

- Added CLI flag `--brf-preflight <txt>` for validating an existing Unicode Braille text file.
- Preflight mode skips the image renderer and emits `mode=BRF_PREFLIGHT`.
- Preflight reports include the source TXT path in the artifact manifest.
- Strict preflight returns exit code `2` when diagnostics are present.
- Render schema remains `1.11` because the report uses the existing artifact manifest and `brf_export` contract.

## Install

```bash
pip install -e ".[dev]"
```

## CLI usage

Render an input image in tactile mode:

```bash
braille-dotmatrix input.png \
  --width-cells 100 \
  --mode TACTILE \
  --output-png artifacts/output_braille.png \
  --output-txt artifacts/output_braille.txt \
  --report-json artifacts/render_report.json
```

Render tactile mode and add a BRF-like artifact:

```bash
braille-dotmatrix input.png \
  --mode TACTILE \
  --output-brf artifacts/output_braille.brf \
  --brf-profile a4-40x25 \
  --report-json artifacts/render_report.json
```

Validate BRF diagnostics after rendering:

```bash
braille-dotmatrix input.png \
  --mode TACTILE \
  --brf-validate-only \
  --brf-print-summary \
  --report-json artifacts/render_report.json
```

Validate an existing Unicode Braille text file:

```bash
braille-dotmatrix \
  --brf-preflight artifacts/output_braille.txt \
  --brf-profile a4-40x25 \
  --brf-print-summary \
  --report-json artifacts/brf_preflight_report.json
```

Run smoke benchmarks:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

## Python API

```python
from braille_dotmatrix_engine import build_embosser_profile, unicode_braille_to_brf_text, write_brf_text
from braille_dotmatrix_engine.brf import validate_brf_text

profile = build_embosser_profile("a4-40x25")
result = unicode_braille_to_brf_text("⠁⠃⠉", profile)
print(result.text)
print(result.report["summary"])
write_brf_text("⠁⠃⠉", "artifacts/output.brf", profile)
print(validate_brf_text("⠁⠃⠉", profile)["summary"])
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

## Outputs

| Output | Purpose |
|---|---|
| `.png` | tactile black/white raster, monochrome screen preview, chromatic preview, or true ASCII preview artifact depending on mode |
| `.txt` | copyable Unicode Braille or ASCII art text |
| `.html` | browser-previewable ASCII art using monospace layout |
| `.json` | render/preflight report and artifact manifest |
| `.svg` | physical millimeter-space tactile vector export |
| `.csv` | benchmark runtime / memory / quality table |
| `.brf` | six-dot Braille ASCII / BRF-like text export target |

## Version and schema policy

Package version, render schema version, and benchmark schema version are intentionally independent. `v1.20.0` keeps render schema at `1.11`.

## Design direction

```text
V1 Braille + ASCII Multi-Symbol Renderer
↓
V2 Semantic Braille Engine
↓
V3 Tactile Graphics Quality Engine
↓
V4 Visual Semantic Encoding Layer
```

See [`ROADMAP.md`](ROADMAP.md), [`docs/ROADMAP_V2.md`](docs/ROADMAP_V2.md), [`docs/PROJECT_DESIGN.md`](docs/PROJECT_DESIGN.md), [`docs/RESEARCH_NOTES.md`](docs/RESEARCH_NOTES.md), and [`docs/VERSION_PLAN.md`](docs/VERSION_PLAN.md).

## Tests

```bash
pytest -q
```

## License

MIT
