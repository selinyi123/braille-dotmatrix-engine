# v1.31.0 Agent Workflow — Attestation verification checklist

## Objective

Make release artifact attestation verification explicit and reviewable without expanding pull request CI permissions.

## Agents

### 1. Research Agent

- Review GitHub CLI attestation verification behavior.
- Distinguish online verification from offline or air-gapped verification.
- Keep this slice focused on release verification checklist generation.

### 2. Repo Audit Agent

- Confirm v1.30.0 release attestation workflow exists.
- Confirm release workflow does not run on pull requests.
- Confirm release artifacts include wheel, sdist, BRF JSON artifacts, provenance, and attestation plan.

### 3. Implementation Agent

- Add release verification checklist helper.
- Generate one `gh attestation verify` command per planned release subject.
- Include manual release checks and online/offline verification notes.

### 4. CI Boundary Agent

- Update release workflow to generate `release_verification_checklist.json`.
- Include the checklist in the attested subject list and uploaded release bundle.
- Do not change normal test workflow permissions.

### 5. QA Agent

- Add helper tests and workflow boundary tests.
- Confirm standard PR CI passes.
- Confirm schema versions remain unchanged.

### 6. Release Agent

- Open a focused PR.
- Wait for CI.
- Address review comments.
- Merge only after success.

## Next workflow target

`v1.32.0` should evaluate release notes automation or offline verification bundle planning.
