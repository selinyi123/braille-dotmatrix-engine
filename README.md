# Braille Dot-Matrix Engine

Industrial Unicode Braille and ASCII visual-symbol rendering engine for tactile graphics, monochrome previews, colored dot-matrix art, HTML previews, CI benchmark artifacts, and benchmarkable rendering experiments.

The project converts images into a physical 2x4 dot lattice and multiple text/visual encodings: Unicode Braille, tactile PNG/SVG, chromatic previews, ASCII mono/color text, HTML ASCII previews, validation reports, quality reports, and benchmark CSV/JSON artifacts.

## Current version

`v1.31.0`

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
- BRF batch contract normalization for generated reports
- structured JSON report diff helper for contract drift review
- blocking BRF contract drift policy after diagnostic artifact upload
- intentional contract migration review records with required reasons
- release-only artifact attestation boundary for wheel, sdist, and BRF release artifacts
- release attestation plan JSON with subject hashes and sizes
- release verification checklist JSON with `gh attestation verify` commands
- SHA-256 artifact provenance manifest generation
- BRF batch CI report artifact upload with provenance manifest
- benchmark profiles for smoke, medium, and stress image sizes
- ASCII charset presets, ASCII PNG previews, and optional HTML export
- centralized render, BRF, and benchmark schema constants
- centralized configuration validation before rendering
- input image file-size and pixel-count resource limits
- shared runtime direct-API validation helpers
- tactile output validation for spacing, active-dot collisions, and occupancy
- deterministic seed path for density correction
- CI test scaffold

### v1.31.0 release verification notes

- Added `braille_dotmatrix_engine.release_verification`.
- Added `build_release_verification_checklist()` and `write_release_verification_checklist()`.
- Added `python -m braille_dotmatrix_engine.release_verification` CLI entry point.
- Release workflow now writes `release_verification_checklist.json` from `release_attestation_plan.json`.
- The checklist records one `gh attestation verify ... -R owner/repo` command per release subject.
- The checklist also records online/offline verification notes and manual release checks.
- `release_verification_checklist.json` is included in the attested release subject list.

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

Normalize a generated BRF batch report into the checked-in contract shape:

```bash
python -m braille_dotmatrix_engine.brf_contract artifacts/brf/brf_batch_report.json --output artifacts/brf/brf_batch_contract.json
```

Compare two JSON reports:

```bash
braille-dotmatrix --report-diff-old examples/brf/snapshots/batch_examples.json --report-diff-new artifacts/brf/brf_batch_contract.json --report-json artifacts/brf/report_diff.json --report-diff-print-summary
```

Evaluate and enforce a report diff policy:

```bash
python -m braille_dotmatrix_engine.report_diff_policy artifacts/brf/report_diff.json --output artifacts/brf/drift_policy.json --enforce
```

Create a reviewed contract migration record. `--reason` is required when the proposed contract differs from the current contract:

```bash
python -m braille_dotmatrix_engine.contract_migration \
  examples/brf/snapshots/batch_examples.json \
  artifacts/brf/brf_batch_contract.json \
  --output artifacts/brf/contract_migration.json \
  --reason "intentional BRF profile contract update"
```

Create a release attestation plan for built release artifacts:

```bash
python -m braille_dotmatrix_engine.release_attestation artifacts/release --output artifacts/release/release_attestation_plan.json
```

Create a release verification checklist from an attestation plan:

```bash
python -m braille_dotmatrix_engine.release_verification \
  artifacts/release/release_attestation_plan.json \
  --output artifacts/release/release_verification_checklist.json \
  --repository selinyi123/braille-dotmatrix-engine
```

Verify an attested release artifact online:

```bash
gh attestation verify artifacts/release/<artifact> -R selinyi123/braille-dotmatrix-engine
```

Generate a SHA-256 artifact provenance manifest:

```bash
python -m braille_dotmatrix_engine.artifact_provenance artifacts/brf --output artifacts/brf/provenance_manifest.json --label brf-batch-report
```

Run smoke benchmarks with CSV and summary artifacts:

```bash
braille-dotmatrix --benchmark --benchmark-csv artifacts/benchmark.csv --benchmark-summary artifacts/benchmark_summary.json
```

## Python API

```python
from pathlib import Path
import json
from braille_dotmatrix_engine.brf_contract import write_batch_contract_from_report
from braille_dotmatrix_engine.contract_migration import propose_contract_migration
from braille_dotmatrix_engine.release_attestation import build_release_attestation_plan
from braille_dotmatrix_engine.release_verification import build_release_verification_checklist
from braille_dotmatrix_engine.report_diff import diff_reports
from braille_dotmatrix_engine.report_diff_policy import evaluate_report_diff_policy

contract = write_batch_contract_from_report("artifacts/brf/brf_batch_report.json", "artifacts/brf/brf_batch_contract.json")
expected = json.loads(Path("examples/brf/snapshots/batch_examples.json").read_text(encoding="utf-8"))
diff = diff_reports(expected, contract)
print(evaluate_report_diff_policy(diff)["status"])
print(propose_contract_migration(expected, contract, reason="intentional update")["status"])
plan = build_release_attestation_plan("artifacts/release")
print(build_release_verification_checklist(plan, repository="selinyi123/braille-dotmatrix-engine")["subject_count"])
```

## JSON contracts

Checked-in BRF report contracts live under:

```text
examples/brf/snapshots/
```

These files intentionally store only stable report fields used for regression tests. When a checked-in contract needs to change intentionally, create a contract migration record with a clear reason and update tests and snapshots in the same PR.

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

CI additionally runs the configured Ruff correctness gate, package build, wheel install smoke, pytest matrix, BRF batch report artifact generation, BRF contract normalization, report diff generation, drift policy evaluation, BRF provenance manifest generation, blocking drift enforcement, and benchmark smoke. Release attestations and release verification checklist generation run only in the separate release workflow.

## License

MIT
