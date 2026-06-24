# v1.28.0 Agent Workflow — Blocking drift policy

## Objective

Make BRF contract drift block CI while preserving diagnostics needed for debugging.

## Agents

### 1. Research Agent

- Check GitHub Actions behavior for step failures, `continue-on-error`, diagnostic upload, and artifact absence handling.
- Keep the scope focused on CI drift policy rather than BRF encoding or report schema redesign.

### 2. Repo Audit Agent

- Confirm main branch already has report diff generation, contract normalization, and provenance manifest support.
- Confirm there are no temporary files or accidental main-branch project artifacts.

### 3. Implementation Agent

- Add a reusable report diff policy helper.
- Keep the policy independent from BRF-specific contract normalization.
- Avoid adding dependencies.

### 4. CI Agent

- Generate report, contract, diff, drift policy, and provenance.
- Upload all diagnostics before enforcing the blocking gate.
- Fail only at the final policy enforcement step.

### 5. QA Agent

- Add API and CLI tests for pass/fail policy behavior.
- Confirm pytest matrix and BRF artifact job pass.
- Confirm artifact includes `drift_policy.json`.

### 6. Release Agent

- Open a focused PR.
- Merge only after CI success and artifact confirmation.
- Report exact commit, CI state, changed files, and next node.

## Next workflow target

`v1.29.0` should formalize intentional contract migration, because blocking drift creates a need for a controlled update process.
