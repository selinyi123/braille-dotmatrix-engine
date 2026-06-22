# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.22.0`

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
- batch BRF preflight for fixture and artifact directories
- checked-in BRF example fixtures for valid, warning, and error cases
- benchmark profiles for smoke, medium, and stress image sizes
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- centralized render/benchmark schema constants
- centralized configuration validation before rendering
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.22.0 BRF batch preflight notes

- Added CLI flag `--brf-preflight-batch <path>`.
- Added `--brf-batch-pattern`, defaulting to `*.txt` for directory inputs.
- Batch reports use `mode=BRF_PREFLIGHT_BATCH`.
- Batch reports include aggregate file counts and per-file summaries.
- Strict batch preflight returns exit code `2` when any file has diagnostics.

## Install

```bash
pip install -e ".[dev]"
```

## CLI usage

Validate one existing Unicode Braille text file:

```bash
braille-dotmatrix \
  --brf-preflight examples/brf/valid_six_dot.txt \
  --brf-print-summary \
  --report-json artifacts/brf_preflight_report.json
```

Validate a directory of Unicode Braille text files:

```bash
braille-dotmatrix \
  --brf-preflight-batch examples/brf \
  --brf-batch-pattern "*.txt" \
  --brf-print-summary \
  --report-json artifacts/brf_batch_report.json
```

Expected fixture aggregate:

```text
files=3; ok=1; warnings=1; errors=1; issue_files=2
```

Run smoke benchmarks:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

## Python API

```python
from pathlib import Path
from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files

paths = resolve_brf_input_paths(Path("examples/brf"), "*.txt")
report = validate_brf_files(paths)
print(report["aggregate"])
```

## Unicode Braille mapping

The engine uses the official physical 8-dot Braille layout:

```text
1 4
2 5
3 6
7 8
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

Package version, render schema version, and benchmark schema version are intentionally independent. `v1.22.0` keeps render schema at `1.11`.

## Tests

```bash
pytest -q
```

## License

MIT
