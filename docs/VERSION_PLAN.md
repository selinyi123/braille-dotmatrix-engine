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

Status: implemented in `feat/v1.11.0-renderer-strategy`.

Goals:

- introduce renderer strategy classes for TACTILE, SCREEN, CHROMATIC, ASCII_MONO, and ASCII_COLOR,
- add `RenderContext` and `RenderResult` contracts,
- add a renderer registry,
- keep `process_image` as orchestration rather than a monolithic mode-branching function,
- expose renderer strategy names in render reports.

Acceptance:

- `process_image` validates config, prepares outputs, loads image, selects renderer, writes report,
- each public mode resolves through `get_renderer`,
- renderer strategy is visible in `report["renderer"]["strategy"]`,
- output artifacts remain compatible with v1.10 reports,
- adding a new renderer can be done through the registry and renderer package instead of editing core orchestration.

## v1.12.0 — Report adapter and artifact writer

Goals:

- introduce `ReportBuilder` or `ReportAdapter` for legacy top-level compatibility fields,
- introduce `ArtifactWriter` for path management and output manifest generation,
- centralize output path semantics for PNG, TXT, SVG, HTML, JSON, and benchmark artifacts,
- prepare optional schema version bump after compatibility audit.

Acceptance:

- renderers return renderer-native reports,
- legacy top-level report fields are generated in one adapter,
- artifact path fields are normalized and tested,
- report schema compatibility is explicitly documented.

## v1.13.0 — Large-image benchmark and memory reporting

Goals:

- add synthetic 1080p and 4K benchmark profiles,
- add estimated peak-memory report,
- add optional stress benchmark profile for 8K images,
- compare tiled sampling behavior across image sizes.

Acceptance:

- medium benchmark runs in CI or scheduled benchmark workflow,
- stress benchmark is available but not mandatory in PR CI,
- render report includes memory-estimate fields.

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
