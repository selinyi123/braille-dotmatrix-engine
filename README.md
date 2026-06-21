# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, terminal text art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.15.0`

## Status

This repository is currently in the **V1 engineering prototype** stage:

- Unicode Braille encoding and decoding
- image-to-dot sampling
- CLAHE preprocessing
- edge-aware Braille sampling enhancement
- Braille density target control and seam diagnostics
- serpentine error-diffusion dithering
- tactile, screen, `CHROMATIC`, `ASCII_MONO`, and `ASCII_COLOR` rendering modes
- renderer strategy runtime for mode-specific output behavior
- artifact manifest and report adapter layer
- generic embosser export boundary for page/device capacity metadata
- conservative six-dot BRF-like text export with compatibility diagnostics
- benchmark profiles for smoke, medium, and stress image sizes
- benchmark memory estimates and artifact-size reporting
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- PNG, TXT, JSON report, optional SVG/HTML export, and benchmark CSV output
- dedicated benchmark smoke job with uploaded benchmark artifacts
- centralized render/benchmark schema constants
- centralized configuration validation before rendering
- Windows-safe benchmark RSS fallback
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.15.0 six-dot text export notes

- Added `unicode_braille_to_brf_text()` for conservative six-dot Unicode Braille to Braille ASCII / BRF-like text export.
- Added `write_brf_text()` for ASCII-safe `.brf` artifact writing.
- Export uses `GenericEmbosserProfile` capacity metadata to wrap lines and paginate with form-feed separators.
- Dots 7 and 8 are reported as unsupported instead of being silently dropped.
- Non-Braille characters are reported with line, column, codepoint, and reason diagnostics.

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

When `--ascii-html` is used without `--output-html`, the engine writes a sibling HTML file next to the ASCII text output.

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

Run smoke benchmarks through the package CLI:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

Run the dedicated benchmark module used by CI:

```bash
python -m braille_dotmatrix_engine.benchmark \
  --profile smoke \
  --output-dir artifacts/benchmarks \
  --csv artifacts/benchmarks/benchmark.csv \
  --summary artifacts/benchmarks/benchmark_summary.json
```

Run larger benchmark profiles manually:

```bash
python -m braille_dotmatrix_engine.benchmark --profile medium --no-ascii
python -m braille_dotmatrix_engine.benchmark --profile stress --no-ascii --max-runtime-sec 300 --max-rss-mb 8192
```

## Python API

```python
from braille_dotmatrix_engine import BrailleArtConfig, process_image

cfg = BrailleArtConfig(
    output_width_cells=100,
    mode="ASCII_MONO",
    ascii_charset_preset="dense",
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

print(report["artifact_manifest"]["png"])
```

Attach Braille diagnostics to ASCII output when needed:

```python
cfg = BrailleArtConfig(
    output_width_cells=100,
    mode="ASCII_MONO",
    include_braille_diagnostics=True,
)
```

Inspect renderer strategies:

```python
from braille_dotmatrix_engine import get_renderer, renderer_names

print(renderer_names())
print(type(get_renderer("TACTILE")).__name__)
```

Inspect generic embosser capacity:

```python
from braille_dotmatrix_engine import GenericEmbosserProfile, embosser_capacity, embosser_export_manifest

profile = GenericEmbosserProfile(name="a4-six-dot")
print(embosser_capacity(profile))
print(embosser_export_manifest(profile, output_path="out.brf", source_artifact="output.txt"))
```

Export six-dot Braille text as a BRF-like artifact:

```python
from braille_dotmatrix_engine import GenericEmbosserProfile, unicode_braille_to_brf_text, write_brf_text

profile = GenericEmbosserProfile(max_cols=40, max_rows=25)
result = unicode_braille_to_brf_text("⠁⠃⠉", profile)
print(result.text)
print(result.report)
write_brf_text("⠁⠃⠉", "artifacts/output.brf", profile)
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
| `.png` | tactile black/white raster, monochrome screen preview, chromatic preview, or true ASCII preview artifact depending on mode |
| `.txt` | copyable Unicode Braille or ASCII art text |
| `.ansi` | ANSI-colored ASCII text |
| `.html` | browser-previewable ASCII art using monospace layout |
| `.json` | render report, metrics, validation status, config, Braille/ASCII quality diagnostics, and artifact manifest |
| `.svg` | physical millimeter-space tactile vector export |
| `.csv` | benchmark runtime / memory / quality table |
| `.brf` | six-dot Braille ASCII / BRF-like text export target |

## Version and schema policy

Package version, render schema version, and benchmark schema version are intentionally independent:

- `package_version`: release/build version of the Python package.
- `schema_version`: JSON render-report schema version.
- `benchmark_schema_version`: benchmark artifact schema version.

A patch release may keep the report schema stable while changing implementation details. `v1.12.0` bumps the render schema because `artifact_manifest` is now part of the report contract. `v1.13.0` bumps the benchmark schema because benchmark rows now include profile, memory-estimate, and artifact-size fields. `v1.14.0` keeps existing schemas stable because embosser support is introduced as a standalone export-boundary API. `v1.15.0` also keeps existing schemas stable because BRF-like export is a standalone API and does not alter render reports or benchmark rows.

## Validation, quality, and benchmark layer

Current validation and quality reporting includes:

- exhaustive 256-pattern Unicode roundtrip
- physical spacing and safety-gap report
- active-dot collision report
- raster roundtrip check for tactile PNG mode
- occupancy and local-density metrics
- Braille density target control
- Braille tile seam diagnostics
- ASCII tone score, edge score, charset preset, PNG preview, and HTML availability
- artifact manifest with path, kind, role, MIME, and existence diagnostics
- generic embosser capacity and export-boundary validation
- six-dot BRF-like export diagnostics for unsupported cells and non-Braille characters
- benchmark CSV artifact with runtime, RSS, occupancy, tone, edge, memory-estimate, artifact-size, profile, and schema fields
- deterministic density correction using `np.random.default_rng(seed)`

## Design direction

The project should not remain only a Braille-art converter. The intended evolution is:

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
