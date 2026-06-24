# v1.27.0 Report diff CI research

## Scope

This pass focuses on CI contract drift visibility for generated BRF batch reports. It does not repeat earlier BRF format, fixture, JSON contract, report diff, artifact upload, or provenance research.

## External findings

- GitHub Actions supports step-level `continue-on-error`, which allows a step to fail without failing the job.
- GitHub Actions status functions such as `always()` are suitable for upload and diagnostics steps that should still run after earlier failures.
- `actions/upload-artifact` supports uploading multiple paths and failing when expected files are missing.
- Workflow research suggests small, focused workflow changes are easier to maintain than large CI rewrites.

## Decision

Implement a non-blocking drift visibility layer:

- normalize the generated full BRF batch report into the checked-in contract shape,
- compare that generated contract against `examples/brf/snapshots/batch_examples.json`,
- always write `report_diff.json`,
- allow the diff command to return non-zero without failing the job,
- upload report, generated contract, diff, and provenance together.

## Policy

For `v1.27.0`, drift reporting is observational. A later release may make drift blocking after the expected contract policy is frozen.
