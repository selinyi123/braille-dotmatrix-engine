# v1.30.0 Release artifact attestation research

## Scope

This pass adds a release-only artifact attestation boundary for Python distribution artifacts and BRF release artifacts. It does not change normal pull request CI permissions.

## External findings

- GitHub Artifact Attestations establish where and how software artifacts were built.
- GitHub's attestation workflow examples require `id-token: write`, `contents: read`, and `attestations: write` permissions for binary artifact attestations.
- GitHub's attestation action accepts `subject-path` for built binary or file artifacts.
- Attestation should be scoped to trusted release boundaries rather than broad pull request CI, because elevated workflow permissions increase the automation attack surface.

## Decision

Add a dedicated `release-attestations` workflow triggered only by:

- manual workflow dispatch
- pushed `v*` tags

The workflow:

1. Builds wheel and sdist.
2. Generates BRF release report artifacts.
3. Enforces BRF contract drift policy.
4. Writes local SHA-256 provenance.
5. Writes a release attestation plan JSON.
6. Generates GitHub Artifact Attestations with `actions/attest@v4`.
7. Uploads the release artifact bundle.

## Non-goals

- No attestation permissions in PR CI.
- No package publishing to PyPI in this slice.
- No registry image attestation.
- No package signing beyond GitHub artifact attestations.

## Next slice

`v1.31.0` should evaluate offline attestation verification documentation or a release checklist that references `gh attestation verify`.
