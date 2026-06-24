# v1.25.0 Version Plan — BRF report diff helper

## Status

Implemented in `work-20260624-b`.

## Goals

- Add dependency-free structured JSON report diffing.
- Support BRF report and batch report drift review.
- Expose Python API and CLI usage.
- Return non-zero from CLI when differences exist.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- API reports matching JSON with zero differences.
- API reports added, removed, and changed nested fields.
- CLI writes diff JSON.
- CLI returns `0` for matching reports and `1` for differing reports.
- Existing quality, pytest, BRF artifact, and benchmark jobs remain green.

## Next version

`v1.26.0 — CI artifact attestation / provenance`

Planned goals:

- Evaluate GitHub artifact attestations.
- Add provenance for release-relevant artifacts where feasible.
- Keep artifact generation transparent and auditable.
