# v1.31.0 Version Plan — Attestation verification documentation and release checklist

## Status

Implemented in `work-20260625-a`.

## Goals

- Add release verification checklist helper.
- Generate `release_verification_checklist.json` from `release_attestation_plan.json`.
- Include one `gh attestation verify` command per release artifact subject.
- Include online and offline verification notes.
- Include the verification checklist in the release artifact bundle.
- Include the verification checklist itself in the attested subject list.
- Keep PR CI permissions unchanged.
- Keep render, BRF, and benchmark schemas unchanged.

## Acceptance

- `build_release_verification_checklist()` emits commands for all planned subjects.
- CLI writes `release_verification_checklist.json`.
- Release workflow generates the verification checklist.
- Release workflow still triggers only on `workflow_dispatch` and `v*` tags.
- Tests verify workflow boundary and subject list.
- Package version is `1.31.0`.

## Next version

`v1.32.0 — Release notes and offline verification bundle planning`

Candidate goals:

- Generate release notes skeleton from release artifacts.
- Document offline attestation verification material requirements.
- Consider an optional verification bundle manifest without changing PR CI permissions.
