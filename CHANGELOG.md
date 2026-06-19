# Changelog

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

### Added

- Expanded README with CLI usage, Python API usage, output types, validation layer, and project direction.
- Added `ROADMAP.md` for V1.4 through V3.0 planning.
- Added `docs/CODE_AUDIT.md` with fixed findings and remaining risks.
- Expanded project design documentation.

### Notes

This release branch focuses on correctness and project foundation rather than adding large new rendering features.
