# v1.29.0 Agent Workflow — Intentional contract migration

## Objective

Create a safe path for intentional JSON contract changes without weakening the blocking drift policy introduced in v1.28.0.

## Agents

### 1. Research Agent

- Review snapshot/golden-file maintenance patterns.
- Review CI maintenance risks around over-complicated workflow changes.
- Keep this slice focused on human-reviewed migration records.

### 2. Repo Audit Agent

- Confirm v1.28.0 has blocking drift policy and diagnostic artifact upload.
- Confirm contract normalization and report diff helpers are available.
- Confirm no release signing or token-permission changes are required for this slice.

### 3. Implementation Agent

- Add a `contract_migration` module.
- Require migration reasons only when drift exists.
- Include changed paths, diff counts, review checklist, and embedded diff.

### 4. QA Agent

- Add API tests for no-change, drift-with-reason, and drift-without-reason.
- Add CLI tests for successful migration output and missing-reason failure.
- Verify public API exports.

### 5. Review Agent

- Add PR template checklist for contract migrations.
- Confirm migration workflow is explicit and reviewable.

### 6. Release Agent

- Open a focused PR.
- Wait for CI.
- Address review comments.
- Merge only after success.

## Next workflow target

`v1.30.0` should evaluate release-only artifact attestations or signed provenance boundaries.
