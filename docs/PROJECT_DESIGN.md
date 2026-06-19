# Project Design

## Positioning

`braille-dotmatrix-engine` should be treated as a layered rendering and encoding system, not only as an image-to-character-art converter.

The current V1 layer is a Unicode Braille renderer. The long-term target is a semantic tactile graphics engine.

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
Tactile/screen/vector exports
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
| `config.py` | Configuration dataclasses for geometry, material, printer, and pipeline parameters. |
| `preprocess.py` | CLAHE preprocessing and float normalization. |
| `sampling.py` | Dot-grid generation, Gaussian sampling, and tile/overlap sampling. |
| `dither.py` | Atkinson/Stucki/JJN dithering and local density correction. |
| `braille_unicode.py` | Unicode Braille scalar and matrix encode/decode logic. |
| `raster.py` | PNG rendering and raster validation. |
| `vector.py` | SVG tactile export in millimeter coordinates. |
| `metrics.py` | MSE, PSNR, edge score, occupancy, and local-density metrics. |
| `pipeline.py` | End-to-end orchestration and report generation. |
| `cli.py` | Command-line interface. |

## Engineering principles

1. Keep pixel/dot-level numeric work in NumPy, SciPy, and OpenCV.
2. Allow tile-level scheduling loops; avoid pixel-level Python loops in core computation.
3. Keep Unicode Braille mapping exhaustively tested.
4. Separate screen aesthetics from tactile manufacturing constraints.
5. Treat every exported artifact as reproducible from image, config, and seed.

## Known limitations

- Current semantic awareness is not implemented yet.
- Tactile validation is basic and does not yet simulate real fingertip readability.
- Dithering uses sequential error diffusion; this is correct for the algorithm but not fully vectorized.
- Raster drawing still uses PIL drawing loops; acceptable for V1, but a NumPy/OpenCV rasterizer is preferred for V1.5+.
- SVG output exports circles but does not yet emit embossing-machine-specific formats.

## Next architecture target

The next major architectural change should introduce a semantic region map with these fields: label, binary mask, importance score, and rendering policy.

This allows text, line art, and natural-image areas to use different tactile rendering strategies.
