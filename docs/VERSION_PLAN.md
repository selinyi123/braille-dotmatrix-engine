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

Status: merged to `main`.

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

Status: merged to `main`.

Goals:

- introduce a generic embosser profile separate from the tactile renderer,
- represent six-dot, eight-dot, and graphics-mode output policies,
- add page layout metadata: paper size, margins, DPI, dot pitch, and row/column limits,
- expose a capacity report and export manifest before adding concrete device drivers,
- document BRF/Braille ASCII, Unicode Braille, and graphics-mode boundaries.

Acceptance:

- device export remains optional and does not pollute renderer core,
- generic profiles compute printable area and cells per page,
- export manifests describe encoding family and whether a device driver is required,
- tests cover generic six-dot export, graphics-mode export, and invalid profile validation.

## v1.15.0 — BRF text export prototype

Status: merged to `main`.

Goals:

- add a conservative six-dot BRF/Braille ASCII export path,
- keep eight-dot and graphics mode separate from the portable text exporter,
- add pagination by embosser profile capacity,
- report incompatible cells and fallback behavior,
- provide ASCII-safe artifact writing.

Acceptance:

- compatible Unicode Braille text can become a paginated plain text export,
- incompatible cells are reported rather than silently changed,
- tests cover mapping, pagination, unsupported-cell diagnostics, and file writing.

## v1.16.0 — BRF artifact integration

Status: merged to `main`.

Goals:

- expose BRF export through CLI and pipeline-adjacent artifact helpers,
- add report artifact manifest entries for BRF outputs,
- support explicit BRF rows/columns parameters through embosser profiles,
- keep non-portable graphics-mode export separate,
- bump render schema to `1.11` for the BRF artifact manifest entry.

Acceptance:

- CLI can write a BRF-like artifact from compatible Braille text,
- reports can reference BRF artifacts without changing renderer semantics,
- diagnostics remain explicit for unsupported 8-dot cells,
- tests cover CLI output, manifest entries, and report JSON updates.

## v1.17.0 — Embosser profile presets

Status: merged to `main`.

Goals:

- provide named page/profile presets for common layout targets,
- support A4, Letter, portable, and interpoint metadata presets,
- add `--brf-profile` while preserving explicit rows/columns overrides,
- keep profile presets independent from vendor drivers,
- keep render schema stable at `1.11`.

Acceptance:

- callers can request a named profile without manually setting rows and columns,
- reports preserve the selected or overridden profile name,
- invalid profiles still fail fast,
- tests cover preset lookup, preset capacity, override behavior, and CLI selection.

## v1.18.0 — BRF diagnostics hardening

Status: merged to `main`.

Goals:

- add strict BRF mode for unsupported cells,
- split warning/error severity for non-Braille, 8-dot, and graphics-mode mismatches,
- expose a compact diagnostics summary for CLI and Python reports,
- preserve non-strict fallback behavior for exploratory rendering,
- keep render schema stable at `1.11`.

Acceptance:

- strict BRF mode can stop file writing when diagnostics are present,
- reports include warning/error counts by reason and severity,
- non-strict mode remains backward compatible,
- tests cover warning/error grouping and strict API behavior.

## v1.19.0 — BRF report ergonomics

Status: merged to `main`.

Goals:

- add a compact CLI diagnostics summary line,
- add optional JSON-only BRF validation mode,
- restore detailed artifact manifest regression coverage,
- document recommended BRF validation workflow,
- keep render schema stable at `1.11`.

Acceptance:

- CLI can validate BRF export diagnostics without writing a BRF file,
- reports include a compact `summary` string,
- detailed regression tests cover artifact kind, MIME, path, and existence contracts,
- validation-only reports preserve `brf_export` without creating a `.brf` artifact.

## v1.20.0 — BRF preflight input mode

Status: implemented in `work-20260621-d`.

Goals:

- validate an existing Unicode Braille text file without rendering an image,
- support a dedicated BRF preflight command path,
- emit JSON report and compact summary from a text-only input,
- keep render pipeline and text validation pipeline separate,
- keep render schema stable at `1.11`.

Acceptance:

- users can validate BRF compatibility before image processing,
- text-only validation skips the image renderer,
- strict and non-strict results are deterministic and scriptable,
- preflight reports preserve source TXT and report JSON artifacts.

## v1.21.0 — BRF fixture and report examples

Goals:

- add example Unicode Braille TXT fixtures,
- add valid six-dot, eight-dot error, and non-Braille warning examples,
- add strict and non-strict report snapshots,
- document release/preflight workflow.

Acceptance:

- examples can be validated through CLI preflight,
- report snapshots are stable enough for regression tests,
- docs show expected summaries for common BRF states.

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
