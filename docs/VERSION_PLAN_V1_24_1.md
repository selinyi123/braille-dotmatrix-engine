# v1.24.1 Version Plan — BRF batch CI artifact workflow

## Status

Implemented in `work-20260624-a`.

## Goals

- Add a dedicated CI job for BRF batch report generation.
- Upload `brf_batch_report.json` as a workflow artifact.
- Validate expected aggregate counts before upload.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- CI runs `braille-dotmatrix --brf-preflight-batch examples/brf`.
- CI writes `artifacts/brf/brf_batch_report.json`.
- CI verifies expected aggregate counts.
- CI uploads artifact named `brf-batch-report`.
- Existing quality, pytest, and benchmark jobs remain green.

## Next version

`v1.25.0 — BRF report diff helper`

Planned goals:

- Add a helper that compares two BRF reports or batch reports.
- Emit changed fields and old/new values.
- Make JSON contract changes easier to review.
