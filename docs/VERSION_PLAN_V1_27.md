# v1.27.0 Version Plan — Report diff CI integration

## Status

Implemented in `work-20260624-d`.

## Goals

- Normalize generated BRF batch reports into checked-in contract shape.
- Compare generated contracts against `examples/brf/snapshots/batch_examples.json` in CI.
- Generate `report_diff.json` in the BRF artifact directory.
- Upload full report, generated contract, diff, and provenance together.
- Keep drift detection non-blocking until policy is finalized.

## Acceptance

- API can normalize a full `BRF_PREFLIGHT_BATCH` report.
- CLI module can write a generated contract JSON file.
- Contract normalization is idempotent for existing contract JSON.
- CI uploads `brf_batch_report.json`, `brf_batch_contract.json`, `report_diff.json`, and `provenance_manifest.json`.
- Existing quality, pytest, BRF artifact, and benchmark jobs remain green.

## Next version

`v1.28.0 — Blocking drift policy or release attestation evaluation`

Candidate goals:

- Decide whether BRF contract drift should fail CI.
- Alternatively, evaluate signed artifact attestations on release/tag workflows only.
