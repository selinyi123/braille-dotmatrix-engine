# v1.26.0 Version Plan — CI artifact provenance manifest

## Status

Implemented in `work-20260624-c`.

## Goals

- Add dependency-free SHA-256 artifact provenance manifests.
- Generate provenance for BRF batch CI artifacts.
- Upload provenance beside `brf_batch_report.json`.
- Avoid adding attestation permissions in PR CI until release behavior is verified.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- API can build a provenance manifest for an artifact directory.
- CLI module can write the manifest to disk.
- Manifest excludes itself when written inside the scanned directory.
- CI validates manifest fields and uploads it.
- Existing quality, pytest, BRF artifact, and benchmark jobs remain green.

## Next version

`v1.27.0 — Report diff CI integration`

Planned goals:

- Compare generated BRF batch report against checked-in JSON contract in CI.
- Generate a report diff artifact when drift exists.
- Keep the workflow non-blocking until drift policy is finalized.
