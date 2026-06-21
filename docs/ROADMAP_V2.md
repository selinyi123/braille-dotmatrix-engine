# Roadmap V2

This roadmap moves the project from a Braille-only renderer into a quality-controlled multi-symbol visual encoding engine and then into a semantic tactile graphics engine.

## v1.9.0 — ASCII and Braille quality controls

- Add ASCII charset presets.
- Add optional HTML ASCII export.
- Add ASCII tone and edge quality metrics.
- Add Braille target-density control.
- Add Braille tile seam diagnostics.
- Keep JSON reports explicit about `ascii_render`, `braille_quality`, and `braille_density_control`.

## v1.10.0 — Benchmark CI hardening

- Upload benchmark CSV and JSON outputs as GitHub Actions artifacts.
- Add a small benchmark smoke job that runs only on synthetic images.
- Track runtime, RSS peak, occupancy, tone, edge, render schema, and benchmark schema metrics.
- Establish conservative baseline thresholds to detect severe regressions.

## v1.10.1 — Output semantics and schema hardening

- Make ASCII-mode PNG output a true ASCII preview artifact.
- Auto-create sibling HTML output when `ascii_html` is enabled without an explicit HTML path.
- Centralize render and benchmark schema constants.
- Add Windows-safe benchmark RSS fallback.
- Add centralized config validation before render execution.

## v1.11.0 — Rasterizer performance

- Replace PIL ellipse loops with an OpenCV or NumPy kernel rasterizer.
- Add a fast path for dense dot grids.
- Keep output determinism identical across Python versions.
- Compare fast rasterizer results against the v1.10 benchmark artifact baseline.

## v2.0.0 — Semantic Braille Engine

- Introduce semantic region maps.
- Split text, line-art, natural-image, and background regions.
- Add region-specific rendering policies.
- Apply importance-weighted dot allocation.
- Report semantic coverage and per-region occupancy.

## v2.1.0 — Tactile graphics quality score

- Define a `Braille Quality Score` with separate tactile, semantic, compression, and manufacturability dimensions.
- Add failure categories for clutter, collision, poor edge continuity, and low subject preservation.

## v3.0.0 — Visual Semantic Encoding Layer

- Export a visual semantic graph alongside Braille/SVG/PNG/ASCII outputs.
- Treat Braille and ASCII as renderers of a general visual semantic runtime.
