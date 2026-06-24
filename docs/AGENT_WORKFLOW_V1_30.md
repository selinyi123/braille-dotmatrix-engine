# v1.30.0 Agent Workflow — Release artifact attestations

## Objective

Add a release-only attestation boundary without increasing pull request CI permissions.

## Agents

### 1. Research Agent

- Review GitHub Artifact Attestation requirements.
- Identify minimum required workflow permissions.
- Keep attestation logic scoped to release/tag boundaries.

### 2. Repo Audit Agent

- Confirm normal PR CI already builds wheels, runs tests, and validates BRF contract drift.
- Confirm release workflow can reuse existing BRF contract and provenance helpers.
- Confirm no PyPI publishing or registry push is included in this slice.

### 3. Implementation Agent

- Add release attestation plan helper.
- Add release-only workflow.
- Keep subject selection deterministic and file-based.

### 4. QA Agent

- Test attestation plan helper.
- Test release workflow trigger and permission boundaries by text inspection.
- Confirm schema constants remain unchanged.

### 5. Release Agent

- Open a focused PR.
- Wait for standard CI.
- Address review comments.
- Merge only after success.

## Next workflow target

`v1.31.0` should document attestation verification and add a release verification checklist.
