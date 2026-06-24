# v1.29.0 Version Plan — Intentional contract migration workflow

## Status

Implemented in `work-20260624-f`.

## Goals

- Add an explicit contract migration review helper.
- Require a non-empty reason when a proposed contract differs from the current checked-in contract.
- Generate a migration JSON record containing diff counts, changed paths, checklist, and embedded diff.
- Add PR checklist items for intentional JSON contract updates.
- Keep v1.28 blocking drift policy intact.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- `propose_contract_migration()` returns `no_change` with no reason when there is no drift.
- Drift without reason raises `ValueError` at API level.
- CLI returns `2` when drift exists but no reason is supplied.
- CLI writes a migration JSON record when drift has a reason.
- PR template includes contract migration checklist.
- Package version is `1.29.0`.

## Next version

`v1.30.0 — Release artifact attestation boundary`

Candidate goals:

- Evaluate GitHub Artifact Attestations for release-only workflows.
- Avoid broadening PR CI token permissions.
- Add documented release provenance policy.
