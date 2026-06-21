# Version Plan

## v1.10.2 — Hardening release

Status: merged to `main`.

Goals:

- reject invalid public configuration before rendering,
- unify PNG and SVG physical radius semantics,
- expose package version in reports,
- add regression tests for validation and geometry consistency,
- document external research and next steps.

Acceptance:

- `pytest -q` passes,
- invalid render modes are rejected,
- invalid dither candidates are rejected,
- invalid geometry/material/chromatic parameters are rejected,
- SVG export uses the same compensated radius policy as PNG output.

## v1.10.3 — Mode-specific pipeline semantics

Status: merged to `main`.

Goals:

- split ASCII mode into a fast path that does not require full Braille diagnostics by default,
- keep optional Braille diagnostics for ASCII through `include_braille_diagnostics=True`,
- split CHROMATIC report semantics from tactile-only roundtrip validation,
- add explicit report sections: `renderer`, `artifacts`, and `diagnostics`,
- keep backward-compatible top-level fields for one minor cycle.

Acceptance:

- ASCII mode renders without Braille dither unless diagnostics are enabled,
- report clearly marks skipped diagnostics,
- ASCII reports keep `ascii_render` and quality metrics,
- CHROMATIC reports show tactile raster roundtrip as skipped,
- existing benchmark smoke workflow remains green.

## v1.11.0 — Renderer strategy architecture

Status: merged to `main`.

Goals:

- introduce renderer strategy classes for TACTILE, SCREEN, CHROMATIC, ASCII_MONO, and ASCII_COLOR,
- add `RenderContext` and `RenderResult` contracts,
- add a renderer registry,
- keep `process_image` as orchestration rather than a monolithic mode-branching function,
- expose renderer strategy names in render reports.

Acceptance:

- `process_image` validates config, prepares outputs, loads image, selects renderer, writes report,
- each public mode resolves through `get_renderer`,
- renderer strategy is visible in render reports,
- output artifacts remain compatible with v1.10 reports,
- adding a new renderer can be done through the registry and renderer package instead of editing core orchestration.

## v1.12.0 — Report adapter and artifact manifest

Status: merged to `main`.

Goals:

- introduce artifact manifest generation for PNG, TXT, SVG, HTML, and JSON report outputs,
- centralize output directory preparation,
- introduce report adapter functions for base report creation and renderer report adaptation,
- preserve legacy `artifacts` path fields,
- bump render schema to `1.10` to make the manifest explicit.

Acceptance:

- render reports include `artifact_manifest`,
- legacy `artifacts` path fields remain available,
- artifact entries include path, kind, role, MIME, and existence diagnostics,
- report schema compatibility is tested,
- `process_image` remains orchestration-only.

## v1.13.0 — Large-image benchmark and memory reporting

Status: implemented in `feat/v1.13.0-benchmark-memory`.

Goals:

- add benchmark profiles for smoke, medium, and stress image sizes,
- include 720p and 1080p synthetic benchmark cases in the medium profile,
- include opt-in 4K stress benchmark case,
- add input-pixel, megapixel, memory-estimate, and artifact-size fields,
- bump benchmark schema to `1.11`.

Acceptance:

- PR CI continues to run the smoke profile,
- medium and stress profiles are available from the benchmark CLI,
- benchmark CSV includes memory-estimate and artifact-size fields,
- benchmark summary includes max estimated working set and total artifact bytes,
- validation checks benchmark schema compatibility.

## v1.14.0 — Embosser and tactile device export boundary

Goals:

- introduce an embosser/exporter abstraction separate from the tactile renderer,
- represent 6-dot, 8-dot, and graphics-mode output policies,
- add page layout metadata: paper size, margins, DPI, dot pitch, and row/column limits,
- research SVG-to-embosser and BrailleRAP-style output paths.

Acceptance:

- device export remains optional and does not pollute renderer core,
- report artifacts can describe page/device metadata,
- tests cover at least one generic embosser profile.

## v2.0.0 — Semantic Braille Engine

Goals:

- introduce semantic region map schema,
- support text, line-art, natural-image, background, and chart-region labels,
- add region-specific tactile policy,
- apply importance-weighted dot allocation.

Acceptance:

- pipeline can consume a semantic map,
- report includes region coverage and per-region occupancy,
- semantic regions can change tactile output density and edge preservation.

## v2.1.0 — Tactile quality score

Goals:

- define tactile quality score dimensions: manufacturability, readability, semantic preservation, clutter, edge continuity,
- add failure categories,
- add quality snapshots for benchmark artifacts.

Acceptance:

- each render receives a structured quality score,
- reports include actionable failure categories,
- tests cover high-clutter and low-edge-continuity cases.
