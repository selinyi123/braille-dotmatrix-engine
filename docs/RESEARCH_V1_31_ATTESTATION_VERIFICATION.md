# v1.31.0 Attestation verification research

## Scope

This pass documents and automates the verification side of the release attestation boundary introduced in v1.30.0.

## External findings

- GitHub documents `gh attestation verify PATH -R OWNER/REPO` for online binary artifact attestation verification.
- GitHub also documents a separate offline and air-gapped verification path.
- Verification should be explicit in release artifacts, not implicit tribal knowledge.
- A release workflow can generate a verification checklist without increasing pull request CI permissions.

## Decision

Add a release verification checklist helper that consumes `release_attestation_plan.json` and emits:

- one `gh attestation verify` command per release artifact subject,
- expected artifact path,
- SHA-256 hash copied from the release attestation plan,
- online verification note,
- offline verification boundary note,
- manual release checklist.

The release workflow now writes `release_verification_checklist.json` and includes it in both the attested subject list and uploaded release artifact bundle.

## Non-goals

- No PR CI attestation verification.
- No offline verification bundle generation in this version.
- No PyPI publishing.
- No release signing beyond GitHub artifact attestations.

## Next slice

`v1.32.0` should add release notes automation or offline verification bundle planning if the release workflow is stable.
