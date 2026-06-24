# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.23.0`

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
- optional recursive BRF batch directory scans
- checked-in BRF example fixtures for valid, warning, and error cases
- JSON contract fixtures for BRF report regression tests
- benchmark profiles for smoke, medium, and stress image sizes
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- centralized render, BRF, and benchmark schema constants
- centralized configuration validation before rendering
- shared runtime direct-API validation helpers
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.23.x schema notes

- Render report schema remains `1.11`.
- BRF-specific reports use `brf_schema_version`.
- Benchmark reports use their own benchmark schema version.
- Package version, render schema, BRF schema, and benchmark schema are intentionally independent.

## Install

```bash
pip install -e ".[dev]"
```

## CLI usage

Validate one existing Unicode Braille text file:

```bash
braille-dotmatrix --brf-preflight examples/brf/valid_six_dot.txt --brf-print-summary --report-json artifacts/brf_preflight_report.json
```

Validate a directory of Unicode Braille text files. Directory scanning is non-recursive by default:

```bash
braille-dotmatrix --brf-preflight-batch examples/brf --brf-batch-pattern "*.txt" --brf-print-summary --report-json artifacts/brf_batch_report.json
```

Recursively scan a directory:

```bash
braille-dotmatrix --brf-preflight-batch examples/brf --brf-batch-recursive --brf-batch-pattern "*.txt" --report-json artifacts/brf_batch_recursive_report.json
```

Run smoke benchmarks:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv
```

## Python API

```python
from pathlib import Path
from braille_dotmatrix_engine.brf import validate_brf_text
from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files

single = validate_brf_text(Path("examples/brf/valid_six_dot.txt").read_text(encoding="utf-8"))
paths = resolve_brf_input_paths(Path("examples/brf"), "*.txt")
batch = validate_brf_files(paths)
print(single["summary"])
print(batch["aggregate"])
```

## JSON contracts

Checked-in BRF report contracts live under:

```text
examples/brf/snapshots/
```

These files intentionally store only stable report fields used for regression tests.

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

Package version, render schema version, BRF schema version, and benchmark schema version are intentionally independent. A package release may include internal hardening without changing the render schema, while BRF or benchmark reports may evolve independently.

## Tests

```bash
pytest -q
```

CI additionally runs the configured Ruff correctness gate, package build, wheel install smoke, pytest matrix, and benchmark smoke.

## License

MIT
