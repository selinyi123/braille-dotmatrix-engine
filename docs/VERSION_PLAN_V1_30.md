# v1.30.0 Version Plan — Release artifact attestation boundary

## Status

Implemented in `work-20260624-h`.

## Goals

- Add a release-only GitHub Artifact Attestation workflow.
- Keep PR CI permissions unchanged.
- Build wheel and sdist inside the release workflow.
- Generate BRF release report artifacts and enforce contract drift policy.
- Generate local SHA-256 provenance and a release attestation plan JSON.
- Attest release artifacts using `actions/attest@v4`.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- Release workflow triggers only on `workflow_dispatch` and `v*` tags.
- Release workflow requests only `contents: read`, `id-token: write`, and `attestations: write`.
- Release workflow does not run on `pull_request`.
- Release attestation plan helper collects wheel, sdist, and BRF release artifacts.
- Release attestation plan helper records SHA-256 hashes and sizes.
- Tests cover helper output and workflow boundary.
- Package version is `1.30.0`.

## Next version

`v1.31.0 — Attestation verification documentation and release checklist`

Candidate goals:

- Document `gh attestation verify` usage.
- Add release checklist for generated provenance and attestation plan artifacts.
- Consider offline verification notes without expanding CI permissions.
