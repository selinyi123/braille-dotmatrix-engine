# Agent Workflows

This repository uses a small, repeatable agent-style workflow for hardening and feature work. The goal is to keep changes reviewable while still allowing autonomous repair passes.

## Workflow roles

| Role | Scope | Output |
|---|---|---|
| Audit Agent | Read changed and adjacent modules, identify concrete failure modes, classify P0/P1/P2. | Issue list, affected files, expected tests. |
| Fix Agent | Apply minimal code changes that remove the failure mode without broad rewrites. | Focused commits on a feature branch. |
| Contract Agent | Add or update tests, fixtures, and report contracts. | Regression tests and stable JSON snapshots. |
| Performance Agent | Check dot-grid limits, benchmark smoke output, artifact size, and memory-sensitive loops. | Benchmark rows and resource-limit tests. |
| Release Gate Agent | Verify CI, package build, wheel install smoke, and docs/README consistency. | Merge recommendation or follow-up fix list. |

## Branch policy

1. Never write directly to `main` for repairs.
2. Use a short branch name with a version or intent, for example:
   `fix/v1-23-2-api-consistency-schema`.
3. Keep commits grouped by concern:
   - strict JSON / report correctness
   - CLI mode safety
   - BRF / embosser boundary validation
   - renderer direct API hardening
   - schema/version governance
   - tests / CI / docs

## Required checks before merge

Every PR should satisfy:

```bash
ruff check .
pytest -q --cov=braille_dotmatrix_engine --cov-report=term-missing
python -m build
```

`ruff check .` currently uses the repository's configured `select = ["F"]`, so it is a Pyflakes/correctness gate rather than a full style, import-sort, modernization, or complexity gate. Broader Ruff rule enablement should be done in a separate formatting/cleanup PR.

The GitHub Actions workflow also performs a wheel install smoke test:

```bash
braille-dotmatrix --help
```

## Repair loop

1. Reproduce or reason about the failure mode.
2. Add a regression test that fails on the old behavior.
3. Patch the smallest responsible module.
4. Make report artifacts strict-JSON safe.
5. Re-run or rely on CI for the full matrix.
6. If CI fails, inspect the failed job first; do not stack speculative changes.

## Performance guardrails

- All dot-grid generation must respect `max_total_dots` before allocating large arrays.
- Direct renderer APIs must reject non-2D binary matrices and empty inputs.
- BRF batch workflows must cap file count, file size, and retained diagnostics.
- Benchmark smoke should remain lightweight enough for normal PR CI.
- Recursive directory scans should not be introduced without explicit file-count and byte-count tests.

## Release checklist

- Version changes must update README only when intentionally cutting a release.
- Render schema, BRF schema, and benchmark schema versions should change only when their JSON contracts change.
- BRF contract fixtures should be updated only for stable contract fields, not incidental runtime metadata.
