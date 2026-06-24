from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

from .geometry import compensated_dot_radius_mm
from .runtime_validation import as_binary_matrix, require_int_positive


def _render_spacing_px(cfg) -> int:
    return require_int_positive('render_spacing_px', getattr(cfg, 'render_spacing_px', 10))


def _dot_radius_px(cfg):
    radius_mm = compensated_dot_radius_mm(cfg)
    return max(1, int(round((radius_mm / cfg.dot_spacing_mm) * _render_spacing_px(cfg))))


def render_tactile_png(binary, cfg, path):
    b = as_binary_matrix(binary, cfg)
    spacing = _render_spacing_px(cfg)
    image = Image.new('L', (b.shape[1] * spacing, b.shape[0] * spacing), 255)
    draw = ImageDraw.Draw(image)
    radius = _dot_radius_px(cfg)
    for y, x in np.argwhere(b):
        cx = int((x + 0.5) * spacing)
        cy = int((y + 0.5) * spacing)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=0)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def render_screen_png(binary, cfg, path):
    b = as_binary_matrix(binary, cfg)
    spacing = _render_spacing_px(cfg)
    image = Image.new('L', (b.shape[1] * spacing, b.shape[0] * spacing), 0)
    draw = ImageDraw.Draw(image)
    radius = _dot_radius_px(cfg)
    for y, x in np.argwhere(b):
        cx = int((x + 0.5) * spacing)
        cy = int((y + 0.5) * spacing)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=255)
    mask = np.asarray(image, dtype=np.float32) / 255.0
    sigma = max(float(getattr(cfg, 'screen_glow_sigma', 2.2)), 0.1)
    glow = gaussian_filter(mask, sigma=sigma)
    glow = np.clip(glow / max(float(glow.max()), 1e-6), 0, 1)
    ink = 1.0 - 0.92 * mask[..., None]
    warm = np.stack([1.0 - 0.18 * glow, 1.0 - 0.28 * glow, 1.0 - 0.45 * glow], axis=-1)
    out = np.clip(ink * warm, 0, 1)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((out * 255).astype(np.uint8)).save(path)


def render_braille_png(binary, cfg, path):
    if cfg.mode == 'SCREEN':
        render_screen_png(binary, cfg, path)
    else:
        render_tactile_png(binary, cfg, path)


def physical_compliance_check(binary, cfg):
    as_binary_matrix(binary, cfg)
    gap = cfg.dot_spacing_mm - cfg.dot_diameter_mm
    issues = [] if gap >= cfg.safety_gap_mm else [f'Edge gap {gap:.3f} mm < safety gap {cfg.safety_gap_mm:.3f} mm']
    if cfg.dot_diameter_mm <= 0:
        issues.append('Dot diameter must be positive')
    if cfg.dot_spacing_mm <= 0:
        issues.append('Dot spacing must be positive')
    return {'compliant': not issues, 'issues': issues, 'edge_gap_mm': gap, 'compensated_dot_radius_mm': compensated_dot_radius_mm(cfg)}


def raster_roundtrip_check(binary, png_path, cfg):
    expected = as_binary_matrix(binary, cfg)
    img = np.asarray(Image.open(png_path).convert('L'))
    recovered = np.zeros_like(expected)
    spacing = _render_spacing_px(cfg)
    for y in range(expected.shape[0]):
        for x in range(expected.shape[1]):
            cy = int((y + 0.5) * spacing)
            cx = int((x + 0.5) * spacing)
            patch = img[max(0, cy-1):cy+2, max(0, cx-1):cx+2]
            recovered[y, x] = patch.mean() < 180
    mismatches = int(np.count_nonzero(expected != recovered))
    return {'ok': mismatches == 0, 'mismatches': mismatches, 'total': int(expected.size), 'error_rate': mismatches / max(1, int(expected.size))}
