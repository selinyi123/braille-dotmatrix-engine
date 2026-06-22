# v1.23.0 JSON contract research

## Scope

This pass focuses on stable JSON report contracts for the BRF validation layer. It does not repeat earlier BRF format or batch preflight research.

## External findings

- Snapshot-style regression tests are useful when outputs are structured and user-facing.
- Golden JSON files should avoid volatile fields such as absolute paths and timestamps.
- The current BRF report contract is small enough to test with local JSON fixtures rather than adding a dependency.

## Decision

Use checked-in JSON contracts under `examples/brf/snapshots/` and compare them against normalized runtime report dictionaries.

## Next slice

`v1.24.0` should add a CI workflow artifact for the BRF batch report.
