# Roadmap

This roadmap upgrades `braille-dotmatrix-engine` from a Unicode Braille renderer into a semantic tactile graphics pipeline.

## V1.4.0 — Unicode correctness and project foundation

Goal: make the current renderer technically credible.

- Fix official Unicode Braille 8-dot bit layout.
- Add encode/decode matrix roundtrip tests.
- Align README and package versions.
- Document architecture and next-stage design.
- Preserve PNG/TXT/JSON/SVG output paths.

Acceptance:

- `pytest -q` passes.
- All 256 Unicode Braille patterns roundtrip correctly.
- Matrix encode/decode roundtrip passes.

## V1.5.0 — Tactile physical validation hardening

Goal: treat output as a manufacturable tactile artifact, not only a screen image.

Planned work:

- Add dot-collision analysis in physical millimeter coordinates.
- Add minimum diameter and minimum spacing warnings.
- Add occupancy thresholds by local region.
- Add material profiles for PLA, resin, embossing paper, and metal embossing.
- Export validation failures in `render_report.json`.

Acceptance:

- Physical geometry report includes dot collision count.
- Tactile mode blocks invalid exports when configured as strict.
- Tests cover safe and unsafe geometry profiles.

## V1.6.0 — Large-image safe processing

Goal: make 4K/8K usage reliable.

Planned work:

- Add explicit peak-memory estimate to reports.
- Add benchmark script for 512px, 1080p, 4K, and synthetic 8K inputs.
- Add tile seam score.
- Add command-line benchmark mode.

Acceptance:

- `benchmark.csv` is generated.
- 4K path completes without full-image broadcast over the dot-grid pipeline.
- Tile overlap behavior is tested.

## V2.0.0 — Semantic Braille Engine

Goal: move from pixel-first conversion to semantic-weighted tactile graphics.

Planned work:

- Add semantic region abstraction: text, line-art, natural image.
- Add edge-preserving region weights.
- Add text-region high-sharpness binary policy.
- Add background suppression and subject-priority rendering.

Acceptance:

- Region masks are represented in a stable internal schema.
- Text/line-art/natural-image regions can use different pipeline policies.
- Reports include region coverage and per-region occupancy.

## V3.0.0 — Visual Semantic Encoding Layer

Goal: make Braille one renderer among multiple outputs of a visual semantic graph.

Planned work:

- Introduce scene/object graph export.
- Add importance-weighted visual tokens.
- Support downstream renderers: Braille, SVG, HTML preview, and JSON graph.
- Begin dataset collection for tactile recognition feedback.

Acceptance:

- Image processing can output a structured visual semantic graph.
- Braille rendering consumes the graph rather than raw pixels only.
- Reports distinguish semantic loss from raster loss.
