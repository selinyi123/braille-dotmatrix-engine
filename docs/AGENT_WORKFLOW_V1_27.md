# v1.27.0 Agent Workflow — Report diff CI integration

## Objective

Make BRF batch report contract drift visible in CI without prematurely blocking the workflow.

## Agents

### 1. Research Agent

- Check current GitHub Actions behavior for `continue-on-error`, status expressions, and artifact upload.
- Avoid repeating BRF format, fixture, provenance, or report diff research from prior versions.
- Produce implementation constraints before coding.

### 2. Repo Audit Agent

- Inspect current `main` for package version, CI workflow, report diff helper, provenance helper, and checked-in BRF snapshots.
- Detect accidental main-branch writes or temporary files before PR creation.
- Verify that schema versions do not need to change.

### 3. Implementation Agent

- Add a small BRF contract normalization helper.
- Keep generated full reports separate from checked-in compact contract shape.
- Avoid adding dependencies.

### 4. CI Agent

- Generate `brf_batch_report.json`.
- Normalize to `brf_batch_contract.json`.
- Generate `report_diff.json` using the existing report diff CLI.
- Allow drift diff generation to be non-blocking during observation phase.
- Upload report, contract, diff, and provenance together.

### 5. QA Agent

- Add tests for normalization, idempotency, file writing, and module CLI.
- Confirm Ruff, pytest matrix, BRF artifact job, and benchmark smoke all pass.
- Confirm artifact upload includes the expanded file set.

### 6. Release Agent

- Open a focused PR.
- Merge only after CI success and artifact confirmation.
- Report exact commit, CI state, changed files, and next node.

## Next workflow hardening target

`v1.28.0` should decide whether contract drift remains observational or becomes a blocking CI policy.
