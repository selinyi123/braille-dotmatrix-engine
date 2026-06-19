# Quality Controls

This document describes the v1.9.0 quality-control layer.

## ASCII quality controls

The ASCII backend supports charset presets:

- `standard`: compact luminance ramp for general previews.
- `dense`: long ramp for smoother tone mapping.
- `blocks`: block characters for dense terminal previews.
- `binary`: minimal two-level output.

ASCII reports include tone and edge metrics under `ascii_render.quality`.

## HTML ASCII export

Use `--output-html` with `ASCII_MONO` or `ASCII_COLOR` to write a browser-previewable monospace HTML file.

## Braille density control

Use `--braille-target-density` to shift sampled values before dithering toward a target active-dot density.

This is intentionally conservative. It does not rewrite Unicode Braille encoding or the dithering algorithm.

## Braille seam diagnostics

The engine reports tile-level occupancy seam diagnostics under `braille_quality`.

High seam scores indicate visible tile boundaries or abrupt local density discontinuities.
