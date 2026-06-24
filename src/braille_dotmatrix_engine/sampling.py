from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

from .preprocess import float01
from .runtime_validation import require_int_positive, validate_image_shape


def _enforce_dot_grid_limit(cfg, dx: int, dy: int) -> None:
    max_total_dots = require_int_positive('max_total_dots', getattr(cfg, 'max_total_dots', 2_000_000))
    total = int(dx) * int(dy)
    if total > max_total_dots:
        raise ValueError(f'dot grid too large: {total} dots exceeds max_total_dots={max_total_dots}')


def build_dot_grid(cfg, shape):
    h, w = validate_image_shape(shape)
    output_width_cells = require_int_positive('output_width_cells', cfg.output_width_cells)
    dx = max(2, 2 * output_width_cells)
    dy = max(4, int(round((h / max(w, 1)) * dx / 4)) * 4)
    _enforce_dot_grid_limit(cfg, dx, dy)
    spacing = w / dx
    xs = (np.arange(dx) + 0.5) * spacing
    ys = (np.arange(dy) + 0.5) * spacing
    xx, yy = np.meshgrid(xs, ys)
    return np.stack([xx, yy], axis=-1).astype(np.float32), dx, dy, float(spacing)


def gaussian_dot_sampling_flat(img, coords_xy, spacing_px, cfg):
    gray = float01(img)
    coords = np.asarray(coords_xy, dtype=np.float32).reshape(-1, 2)
    sigma = max(((cfg.dot_radius_mm / cfg.dot_spacing_mm) * spacing_px) / 2.0, 0.01)
    blur = gaussian_filter(gray, sigma=sigma, mode='reflect')
    rows = np.clip(coords[:, 1], 0, gray.shape[0] - 1)
    cols = np.clip(coords[:, 0], 0, gray.shape[1] - 1)
    return np.clip(map_coordinates(blur, [rows, cols], order=1, mode='reflect').astype(np.float32), 0, 1)


def gaussian_dot_sampling_grid(img, coords, spacing_px, cfg):
    return gaussian_dot_sampling_flat(img, coords.reshape(-1, 2), spacing_px, cfg).reshape(coords.shape[:2])


def _tile_weights(tile_coords, x0, y0, x1, y1, overlap):
    if overlap <= 0:
        return np.ones(tile_coords.shape[0], dtype=np.float32)
    xs = tile_coords[:, 0]
    ys = tile_coords[:, 1]
    left = np.clip((xs - x0) / overlap, 0.0, 1.0)
    right = np.clip((x1 - xs) / overlap, 0.0, 1.0)
    top = np.clip((ys - y0) / overlap, 0.0, 1.0)
    bottom = np.clip((y1 - ys) / overlap, 0.0, 1.0)
    return np.maximum(np.minimum.reduce([left, right, top, bottom]), 0.05).astype(np.float32)


def process_tiles(img, coords, cfg):
    gray = float01(img)
    h, w = gray.shape
    dy, dx = coords.shape[:2]
    spacing = w / dx
    tile = max(16, cfg.tile_size_px)
    overlap = max(0, min(cfg.tile_overlap_px, tile - 1))
    step = tile - overlap
    values = np.zeros((dy, dx), dtype=np.float64)
    weights = np.zeros((dy, dx), dtype=np.float64)
    border = max(2, int(np.ceil((cfg.dot_radius_mm / cfg.dot_spacing_mm) * spacing * 4)))
    for y0 in range(0, h, step):
        for x0 in range(0, w, step):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            m = (coords[..., 1] >= y0) & (coords[..., 1] < y1) & (coords[..., 0] >= x0) & (coords[..., 0] < x1)
            ys, xs = np.where(m)
            if len(ys) == 0:
                continue
            y0e, y1e = max(0, y0-border), min(h, y1+border)
            x0e, x1e = max(0, x0-border), min(w, x1+border)
            selected = coords[ys, xs]
            samples = gaussian_dot_sampling_flat(gray[y0e:y1e, x0e:x1e], selected - np.array([x0e, y0e]), spacing, cfg)
            wt = _tile_weights(selected.reshape(-1, 2), x0, y0, x1, y1, overlap)
            values[ys, xs] += samples * wt
            weights[ys, xs] += wt
    missing = weights <= 0
    if np.any(missing):
        values[missing] = gaussian_dot_sampling_grid(gray, coords, spacing, cfg)[missing]
        weights[missing] = 1
    return np.clip(values / weights, 0, 1).astype(np.float32)
