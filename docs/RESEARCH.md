# Research notes

## Related open-source direction

Most existing projects around Braille art focus on terminal or ASCII-style rendering. This project should differentiate by treating Unicode Braille output as an auditable rendering artifact rather than only as terminal decoration.

## Technical anchors

- Unicode Braille Patterns cover U+2800 through U+28FF, representing 256 possible 8-dot cells.
- Tactile graphics workflows need spacing, texture, and braille-placement defaults rather than only image thresholding.
- The engine should evolve from image-to-text conversion into a validation-first tactile/screen rendering pipeline.

## Design implication

The moat is not the Unicode mapping itself. The moat is the closed loop:

```text
image -> dot field -> Unicode text -> raster/vector/tactile preview -> reverse validation -> report
```
