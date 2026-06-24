# v1.26.0 Artifact provenance research

## Scope

This pass focuses on artifact provenance for CI-generated JSON outputs. It does not repeat earlier BRF, report diff, or artifact upload research.

## External findings

- GitHub Artifact Attestations establish where and how software artifacts were built.
- Official attestation workflows require additional permissions such as `id-token: write` and `attestations: write`.
- The current repository needs a lower-risk provenance layer that remains stable in pull-request CI.
- A SHA-256 manifest is not equivalent to a signed attestation, but it makes artifact contents auditable and prepares the project for later signed provenance.

## Decision

Implement a dependency-free artifact provenance manifest first:

- recursively scan an artifact directory,
- record relative paths, byte sizes, and SHA-256 digests,
- write the manifest as strict JSON,
- upload it beside the BRF batch report artifact.

## Next slice

`v1.27.0` should integrate report diff into CI to compare generated reports against checked-in contracts and upload a diff artifact on drift.

A later release can evaluate GitHub Artifact Attestations for release artifacts after permission and event-scope behavior are verified.
