# Tactile Export

## Purpose

v1.3 adds a tactile export layer for physical-layout previews and downstream vector workflows.

## SVG output

The engine can export raised-dot layouts as SVG circles in millimeter units.

CLI example:

```bash
braille-dotmatrix input.png --output-svg out.svg
```

API example:

```python
from braille_dotmatrix_engine import BrailleArtConfig, process_image

cfg = BrailleArtConfig(output_width_cells=80)
process_image('input.png', cfg, 'out.png', 'out.txt', 'report.json', 'out.svg')
```

## Report fields

v1.3 reports include:

- `tactile_geometry`: geometry, material, printer, edge gap, cell size, and compliance issues.
- `tactile_export`: SVG path, physical width, physical height, dot count, and geometry report.

## Limitation

The SVG export is a vector dot layout. It is not yet an STL mesh, embossing machine driver, or certified tactile standard validator.
