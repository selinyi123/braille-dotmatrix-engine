from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

def compensated_dot_radius_mm(cfg):
    radius = cfg.dot_radius_mm / max(1 - cfg.material.shrinkage_rate, 1e-6)
    radius += cfg.printer.xy_error_mm * 0.5
    return min(radius, (cfg.dot_spacing_mm - cfg.safety_gap_mm) / 2)

def render_braille_png(binary, cfg, path):
    b = np.asarray(binary, dtype=bool)
    spacing = int(cfg.render_spacing_px)
    image = Image.new('L', (b.shape[1] * spacing, b.shape[0] * spacing), 255)
    draw = ImageDraw.Draw(image)
    radius = max(1, int(round((compensated_dot_radius_mm(cfg) / cfg.dot_spacing_mm) * spacing)))
    for y, x in np.argwhere(b):
        cx = int((x + 0.5) * spacing)
        cy = int((y + 0.5) * spacing)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=0)
    image.save(Path(path))

def physical_compliance_check(binary, cfg):
    gap = cfg.dot_spacing_mm - cfg.dot_diameter_mm
    issues = [] if gap >= cfg.safety_gap_mm else [f'Edge gap {gap:.3f} mm < safety gap {cfg.safety_gap_mm:.3f} mm']
    return {'compliant': not issues, 'issues': issues, 'edge_gap_mm': gap}

def raster_roundtrip_check(binary, png_path, cfg):
    expected = np.asarray(binary, dtype=bool)
    img = np.asarray(Image.open(png_path).convert('L'))
    recovered = np.zeros_like(expected)
    spacing = int(cfg.render_spacing_px)
    for y in range(expected.shape[0]):
        for x in range(expected.shape[1]):
            cy = int((y + 0.5) * spacing)
            cx = int((x + 0.5) * spacing)
            patch = img[max(0, cy-1):cy+2, max(0, cx-1):cx+2]
            recovered[y, x] = patch.mean() < 180
    mismatches = int(np.count_nonzero(expected != recovered))
    return {'ok': mismatches == 0, 'mismatches': mismatches, 'total': int(expected.size), 'error_rate': mismatches / max(1, int(expected.size))}
