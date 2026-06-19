# Project Design

## Positioning

Braille Dot-Matrix Engine is not only a terminal Braille-art converter. It is designed as a validation-first rendering pipeline for Unicode Braille text, tactile-style raster preview, screen preview, and future tactile export formats.

## Core loop

```text
source image -> dot field -> Unicode Braille cells -> rendered preview -> reverse validation -> report
```

## Current architecture

- `config.py`: geometry, material, printer, and runtime configuration.
- `preprocess.py`: image normalization and CLAHE preprocessing.
- `sampling.py`: dot grid construction, Gaussian sampling, tiled processing.
- `dither.py`: Atkinson, Stucki, JJN, adaptive candidate selection.
- `braille_unicode.py`: 8-dot Unicode Braille mapping.
- `raster.py`: tactile and screen PNG rendering plus raster checks.
- `pipeline.py`: end-to-end orchestration.
- `cli.py`: command-line interface.

## Design principles

1. Logical Braille dots must not be changed by printer compensation.
2. Physical compensation belongs to render/export geometry.
3. Unicode roundtrip must remain deterministic.
4. Tactile validation and screen preview should be separate modes.
5. Every version should improve either correctness, validation, export, performance, or UX.

## Near-term design target

v1.x should harden the Python engine. v2.x should add product surfaces such as local web UI, batch jobs, preset profiles, and export bundles.
