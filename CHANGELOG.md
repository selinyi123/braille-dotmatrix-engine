# Changelog

## v1.10.0

### Added

- Added a dedicated `benchmark-smoke` GitHub Actions job.
- Added benchmark artifact upload for generated benchmark CSV, JSON reports, previews, and summary files.
- Added `python -m braille_dotmatrix_engine.benchmark` as a benchmark smoke entry point.
- Added benchmark threshold validation for runtime, RSS peak memory, occupancy, render schema version, and benchmark schema version.
- Added benchmark summary JSON output.
- Extended benchmark tests for validation, summary writing, and module execution.

### Changed

- Updated package version to `1.10.0`.
- Kept render report schema at `1.9`; benchmark rows now include `benchmark_schema_version = 1.10`.
- Expanded project positioning from quality-controlled rendering to CI-validated benchmarkable visual-symbol encoding.

## v1.9.0

### Added

- Added ASCII charset presets: `standard`, `dense`, `blocks`, and `binary`.
- Added optional HTML ASCII export with monospace browser preview.
- Added ASCII tone and edge quality metrics in `ascii_render.quality`.
- Added Braille density target control before dithering.
- Added Braille tile seam diagnostics under `braille_quality`.
- Added CLI options for ASCII presets, HTML export, and Braille target density.
- Added tests for ASCII presets, HTML output, density control, and seam diagnostics.

### Changed

- Updated render report schema to `1.9`.
- Updated package version to `1.9.0`.
- Expanded project positioning from multi-symbol rendering to quality-controlled visual-symbol encoding.

## v1.8.0

### Added

- Added `ASCII_MONO` and `ASCII_COLOR` rendering modes.
- Added `ascii_backend.py` for luminance-to-character mapping and ANSI color ASCII output.
- Added `braille_enhance.py` for edge-aware Braille sampling enhancement before dithering.
- Added ASCII configuration fields and CLI options.
- Added tests for ASCII rendering and Braille enhancement.

### Changed

- Updated render report schema to `1.8`.
- Updated package version to `1.8.0`.
- Extended the project positioning from Braille-only rendering to multi-symbol visual encoding.

## v1.7.1

### Added

- Added the `CHROMATIC` screen rendering backend for colored Gaussian dot-matrix output.
- Added chromatic configuration fields and wired them into the renderer.
- Added `benchmark.py` with smoke benchmarks for tactile and chromatic rendering.
- Added `--benchmark` and `--benchmark-csv` CLI options.
- Added tests for chromatic rendering, benchmark CSV output, and CLI smoke paths.

### Changed

- Updated render report schema to `1.7`.
- Updated package version to `1.7.1`.
- Switched error diffusion to serpentine scanning to reduce directional artifacts.
- Updated documentation and the v2 roadmap.

## v1.5.0

### Added

- Added tactile output validation report for dot spacing, edge gap, active-dot collisions, dot count, and occupancy.
- Added `--strict-tactile` CLI flag to fail tactile-mode export when validation reports errors.
- Added tactile validation output under `validation.tactile_output` in `render_report.json`.
- Added tactile validation regression tests.

### Changed

- Updated render report schema version to `1.5`.
- Bumped package version to `1.5.0`.
- Updated README with strict tactile validation usage.

## v1.4.0

### Fixed

- Corrected Unicode Braille physical 4x2 matrix mapping.
- Added matrix decode path for encode/decode validation.
- Added regression tests for the official 8-dot Unicode bit layout.
- Aligned README and package version.
