from __future__ import annotations

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

_ATKINSON = [(0, 1, 1), (0, 2, 1), (1, -1, 1), (1, 0, 1), (1, 1, 1), (2, 0, 1)]
_STUCKI = [(0, 1, 8), (0, 2, 4), (1, -2, 2), (1, -1, 4), (1, 0, 8), (1, 1, 4), (1, 2, 2), (2, -2, 1), (2, -1, 2), (2, 0, 4), (2, 1, 2), (2, 2, 1)]
_JJN = [(0, 1, 7), (0, 2, 5), (1, -2, 3), (1, -1, 5), (1, 0, 7), (1, 1, 5), (1, 2, 3), (2, -2, 1), (2, -1, 3), (2, 0, 5), (2, 1, 3), (2, 2, 1)]


def _diffuse(img, kernel, div, serpentine: bool = True):
    """Error-diffusion halftoning with optional serpentine scan order.

    Error diffusion is sequential by design because each quantization error is
    propagated into not-yet-visited neighbours. This implementation keeps the
    tiny-kernel neighbour updates scalar; serpentine scanning improves visual
    quality by reducing directional artifacts, not by changing asymptotic speed.
    """
    out = np.asarray(img, dtype=np.float32).copy()
    h, w = out.shape
    same_row = [(dx, wt) for dy, dx, wt in kernel if dy == 0]
    forward_rows: dict[int, list[tuple[int, float]]] = {}
    for dy, dx, wt in kernel:
        if dy > 0:
            forward_rows.setdefault(dy, []).append((dx, wt))

    for y in range(h):
        left_to_right = (not serpentine) or (y % 2 == 0)
        sign = 1 if left_to_right else -1
        xs = range(w) if left_to_right else range(w - 1, -1, -1)
        row = out[y]
        for x in xs:
            old = float(row[x])
            new = 1.0 if old > 0.5 else 0.0
            err = (old - new) / div
            row[x] = new
            for dx, wt in same_row:
                xx = x + sign * dx
                if 0 <= xx < w:
                    row[xx] += err * wt
            for dy, terms in forward_rows.items():
                yy = y + dy
                if yy >= h:
                    continue
                drow = out[yy]
                for dx, wt in terms:
                    xx = x + sign * dx
                    if 0 <= xx < w:
                        drow[xx] += err * wt
    return (out > 0.5).astype(np.float32)


def dither_atkinson(img, serpentine: bool = True):
    return _diffuse(img, _ATKINSON, 8.0, serpentine)


def dither_stucki(img, serpentine: bool = True):
    return _diffuse(img, _STUCKI, 42.0, serpentine)


def dither_jjn(img, serpentine: bool = True):
    return _diffuse(img, _JJN, 48.0, serpentine)


DITHER_MAP = {
    'Atkinson': dither_atkinson,
    'Stucki': dither_stucki,
    'JJN': dither_jjn,
}


def select_best_dither(values, candidates):
    if not candidates:
        raise ValueError('dither_candidates must not be empty')
    proxy = cv2.resize(values, (max(4, values.shape[1] // 4), max(4, values.shape[0] // 4)), interpolation=cv2.INTER_AREA)
    best, best_score = candidates[0], float('inf')
    for name in candidates:
        if name not in DITHER_MAP:
            raise ValueError(f'Unsupported dither method: {name}')
        halftone = DITHER_MAP[name](proxy)
        tone_mse = float(np.mean((proxy - gaussian_filter(halftone, sigma=0.8)) ** 2))
        if tone_mse < best_score:
            best, best_score = name, tone_mse
    return best, DITHER_MAP[best](values)


def correct_over_dense_regions(binary, cfg):
    b = np.asarray(binary, dtype=np.float32).copy()
    density = uniform_filter(b, size=7, mode='reflect')
    over = (density > cfg.max_local_occupancy) & (b > 0)
    if not np.any(over):
        return b
    rng = np.random.default_rng(cfg.seed)
    keep_prob = np.clip(cfg.max_local_occupancy / np.maximum(density, 1e-6), 0, 1)
    keep = rng.random(b.shape) < keep_prob
    b[over & ~keep] = 0
    return b
