# v1.22.0 Version Plan — BRF preflight batch mode

## Status

Implemented in `work-20260622-a`.

## Goals

- Support validating multiple Unicode Braille TXT files in one CLI run.
- Support both single file roots and directory roots.
- Add a glob pattern option for directory runs.
- Emit aggregate counts and per-file summaries.
- Keep render schema stable at `1.11`.

## Acceptance

- `examples/brf/` can be validated as a directory.
- Aggregate report counts total, ok, warning, error, and issue files.
- Per-file summaries remain available for review.
- Strict mode returns exit code `2` when any file has diagnostics.
- CI passes on Python 3.10, 3.11, and 3.12.

## Next version

`v1.23.0 — BRF JSON report snapshots`

Planned goals:

- Add stable JSON snapshot examples.
- Cover strict and non-strict report shapes.
- Lock the `brf_export` and batch report contracts.
