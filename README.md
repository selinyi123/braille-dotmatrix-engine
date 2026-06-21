# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.18.0`

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
- named embosser profile presets for common BRF page capacities
- conservative six-dot BRF-like text export with compatibility diagnostics
- BRF diagnostics summary with warning/error counts and reason grouping
- CLI-level BRF artifact integration and report JSON update path
- benchmark profiles for smoke, medium, and stress image sizes
- benchmark memory estimates and artifact-size reporting
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- PNG, TXT, JSON report, optional SVG/HTML/BRF export, and benchmark CSV output
- dedicated benchmark smoke job with uploaded benchmark artifacts
- centralized render/benchmark schema constants
- centralized configuration validation before rendering
- Windows-safe benchmark RSS fallback
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.18.0 BRF diagnostics hardening notes

- Added BRF diagnostic severity for warning/error classification.
- Added reason grouping through `diagnostics.by_reason` and `diagnostics.by_severity`.
- Added top-level `warning_count` and `error_count` to BRF export reports.
- Added strict BRF mode for Python API and CLI.
- Kept render schema stable at `1.11` because BRF diagnostics live inside the existing `brf_export` report section.

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

Render tactile mode and add a BRF-like artifact with a named profile:

```bash
braille-dotmatrix input.png \
  --width-cells 100 \
  --mode TACTILE \
  --output-png artifacts/output_braille.png \
  --output-txt artifacts/output_braille.txt \
  --output-brf artifacts/output_braille.brf \
  --brf-profile a4-40x25 \
  --report-json artifacts/render_report.json
```

Enable strict BRF diagnostics:

```bash
braille-dotmatrix input.png \
  --mode TACTILE \
  --output-brf artifacts/output_braille.brf \
  --strict-brf
```

Run smoke benchmarks through the package CLI:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

## Python API

```python
from braille_dotmatrix_engine import build_embosser_profile, unicode_braille_to_brf_text, write_brf_text

profile = build_embosser_profile("a4-40x25")
result = unicode_braille_to_brf_text("⠁⠃⠉", profile)
print(result.text)
print(result.report["diagnostics"])
write_brf_text("⠁⠃⠉", "artifacts/output.brf", profile)
```

Strict BRF export:

```python
from braille_dotmatrix_engine.brf import BrfExportError

try:
    write_brf_text("A", "artifacts/output.brf", profile, strict=True)
except BrfExportError as exc:
    print(exc.report["diagnostics"])
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

`v1.18.0` keeps render schema at `1.11` because strict BRF diagnostics are added inside the existing `brf_export` section and do not change the top-level render report contract.

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
- generic embosser capacity, profile presets, and export-boundary validation
- six-dot BRF-like export diagnostics for unsupported cells and non-Braille characters
- BRF diagnostic severity summary by reason and severity
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
