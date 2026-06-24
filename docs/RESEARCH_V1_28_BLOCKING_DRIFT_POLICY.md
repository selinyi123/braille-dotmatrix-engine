# v1.28.0 Blocking drift policy research

## Scope

This pass focuses on turning BRF contract drift from observational CI diagnostics into a blocking CI policy while preserving useful artifacts for debugging.

## External findings

- GitHub Actions supports step-level `continue-on-error`, which allows diagnostic steps to fail without immediately failing a job.
- GitHub Actions expression functions such as `always()` are useful for diagnostic upload steps, but should be applied narrowly.
- `actions/upload-artifact` supports multiple upload paths and `if-no-files-found: error`, which is useful for enforcing diagnostic artifact presence.
- Workflow maintenance research suggests keeping CI changes small and explicit rather than rewriting unrelated workflow areas.

## Decision

Use a staged policy flow:

1. Generate the full BRF batch report.
2. Normalize it into the stable contract shape.
3. Generate `report_diff.json`.
4. Generate `drift_policy.json` from the diff.
5. Generate provenance over the diagnostic files.
6. Upload the full artifact bundle.
7. Enforce the blocking drift policy after upload.

## Rationale

This preserves debug artifacts even when drift eventually fails CI. The policy becomes strict without making failures opaque.

## Next slice

`v1.29.0` should evaluate release-only signed attestations or a manual override mechanism for intentional contract migrations.
