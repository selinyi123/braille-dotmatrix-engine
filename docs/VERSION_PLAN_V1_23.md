# v1.23.0 Version Plan — BRF JSON report contracts

## Status

Implemented in `work-20260622-b`.

## Goals

- Add stable JSON fixtures for BRF report regression tests.
- Cover valid, warning, error, and batch aggregate report shapes.
- Normalize runtime reports before comparison so paths and volatile metadata do not create noisy diffs.
- Keep render schema stable at `1.11`.

## Acceptance

- Valid six-dot report contract is checked.
- Eight-dot error report contract is checked.
- Non-Braille warning report contract is checked.
- Batch aggregate report contract is checked.
- CI passes on Python 3.10, 3.11, and 3.12.

## Next version

`v1.24.0 — BRF batch CI artifact workflow`

Planned goals:

- Add a GitHub Actions job for BRF batch checks over `examples/brf/`.
- Upload the generated batch JSON report as a CI artifact.
- Keep the report contract stable against the v1.23 fixtures.
