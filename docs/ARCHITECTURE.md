# Architecture

## Goal

Braille Dot-Matrix Engine converts images into auditable Unicode Braille dot fields and preview outputs.

## Current modules

```text
cli.py              command-line interface
config.py           runtime configuration and profiles
preprocess.py       image normalization and CLAHE
sampling.py         dot-grid construction and Gaussian dot sampling
dither.py           error-diffusion dithering and density correction
braille_unicode.py  Unicode Braille encode/decode
raster.py           tactile/screen PNG rendering and raster checks
pipeline.py         end-to-end orchestration
engine.py           public compatibility exports
```

## Closed loop

```text
image input
  -> preprocessing
  -> dot sampling
  -> dithering
  -> Unicode Braille matrix
  -> text / PNG / report output
  -> validation checks
```

## Design constraints

- Logical Braille masks must not be mutated by printer compensation.
- Tactile rendering and screen rendering are separate output modes.
- Unicode roundtrip must remain deterministic.
- Raster validation applies to tactile preview, not glow-based screen preview.

## Next architecture split

```text
metrics.py       quality metrics and scoring
validation.py    validation report schema
tactile.py       physical geometry and tactile standards
vector.py        SVG export
benchmarks/      fixture images and performance reports
```
