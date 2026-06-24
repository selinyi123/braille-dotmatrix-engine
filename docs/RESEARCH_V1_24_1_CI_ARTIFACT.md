# v1.24.1 CI artifact research

## Scope

This pass focuses on making BRF batch validation visible as a CI artifact. It does not repeat earlier BRF format, fixture, or JSON contract research.

## External findings

- GitHub Actions artifact upload supports file and directory uploads, `retention-days`, and `if-no-files-found` behavior.
- The upload-artifact v4+ family does not support repeatedly uploading to the same artifact name from multiple jobs.
- For this repository, a dedicated artifact name is safer than appending BRF reports into existing pytest or benchmark artifacts.

## Decision

Add a dedicated `brf-batch-report` job to `.github/workflows/tests.yml`.

The job should:

- install the package with dev dependencies,
- run `braille-dotmatrix --brf-preflight-batch examples/brf`,
- write `artifacts/brf/brf_batch_report.json`,
- assert the expected aggregate fields,
- upload the JSON as `brf-batch-report` with short retention.

## Next slice

`v1.25.0` should add a BRF report diff helper for explaining contract changes.
