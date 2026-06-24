# Project Design

## Positioning

`braille-dotmatrix-engine` should be treated as a layered rendering and encoding system, not only as an image-to-character-art converter.

The current V1 layer is a Unicode Braille, ASCII, chromatic preview, and BRF boundary engine. The long-term target is a semantic tactile graphics engine.

## Pipeline

```text
Image
↓
Preprocess
↓
Dot sampling
↓
Dither and density correction
↓
Unicode Braille encoding
↓
Tactile/screen/chromatic/ASCII/vector/BRF-adjacent exports
↓
Validation report
```

Future versions should insert a semantic layer before rendering:

```text
Image
↓
Semantic region analysis
↓
Region-specific tactile policy
↓
Braille/tactile rendering
```

## Current module map

| Module | Responsibility |
|---|---|
| `config.py` | Configuration dataclasses for geometry, material, printer, rendering, ASCII, chromatic, and resource-limit parameters. |
| `validation.py` | Central validation gate for public configuration values. |
| `runtime_validation.py` | Shared strict direct-API runtime validation helpers for finite numbers, integral dimensions, and binary matrices. |
| `preprocess.py` | Image input normalization, grayscale conversion, and CLAHE preprocessing. |
| `sampling.py` | Dot-grid generation, Gaussian sampling, and tile/overlap sampling. |
| `dither.py` | Atkinson/Stucki/JJN dithering and local density correction. |
| `braille_unicode.py` | Unicode Braille scalar and matrix encode/decode logic. |
| `braille_enhance.py` | Pre-dither Braille value enhancement. |
| `braille_quality.py` | Density control and seam/density quality analysis. |
| `ascii_backend.py` | ASCII mono/color text, ANSI, HTML, and PNG preview generation. |
| `chromatic.py` | Chromatic dot-matrix preview rendering. |
| `raster.py` | PNG rendering and raster validation. |
| `vector.py` | SVG tactile export in millimeter coordinates. |
| `tactile.py` | Physical tactile geometry reports and active-dot validation. |
| `geometry.py` | Manufacturing-compensated dot radius calculations. |
| `metrics.py` | MSE, PSNR, edge score, occupancy, and local-density metrics. |
| `renderers/` | Renderer strategy registry and mode-specific orchestration. |
| `artifacts.py` | Artifact manifests and output directory preparation. |
| `reports.py` | Render report base/adaptation layer. |
| `brf.py` | Six-dot Braille ASCII / BRF-like conversion and diagnostics. |
| `brf_batch.py` | Batch BRF preflight, aggregation, recursion option, and resource limits. |
| `embosser.py` | Generic embosser profile, capacity, and export boundary metadata. |
| `benchmark.py` | Benchmark profiles, runtime/memory/artifact metrics, and summary artifacts. |
| `json_utils.py` | Strict JSON serialization for reports and CLI output. |
| `cli.py` | Command-line interface for rendering, benchmarks, and BRF preflight modes. |

## Engineering principles

1. Keep pixel/dot-level numeric work in NumPy, SciPy, and OpenCV.
2. Allow tile-level scheduling loops; avoid pixel-level Python loops in core computation.
3. Keep Unicode Braille mapping exhaustively tested.
4. Separate screen aesthetics from tactile manufacturing constraints.
5. Treat every exported artifact as reproducible from image, config, and seed.
6. Make all reports strict-JSON safe for dashboards and contract tests.
7. Guard direct public-ish APIs, not only the end-to-end pipeline.
8. Route repeated runtime validation through shared helpers instead of module-local copies.

## Known limitations

- Current semantic awareness is not implemented yet.
- Tactile validation is basic and does not yet simulate real fingertip readability.
- Dithering uses sequential error diffusion; this is correct for the algorithm but not fully vectorized.
- Raster drawing still uses PIL drawing loops; acceptable for V1, but a NumPy/OpenCV rasterizer is preferred for V1.5+.
- SVG output exports circles but does not yet emit embossing-machine-specific formats.
- Benchmarking records point-in-time smoke metrics, not longitudinal trend baselines.
- ASCII diagnostic mode and ASCII fast path still share concepts across two renderer paths and should be unified in a later cleanup.

## Next architecture target

The next major architectural change should introduce a semantic region map with these fields: label, binary mask, importance score, and rendering policy.

This allows text, line art, and natural-image areas to use different tactile rendering strategies.
