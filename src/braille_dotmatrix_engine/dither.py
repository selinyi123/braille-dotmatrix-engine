import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

def _diffuse(img, kernel, div):
    out = np.asarray(img, dtype=np.float32).copy()
    h, w = out.shape
    for y in range(h):
        for x in range(w):
            old = float(out[y, x])
            new = 1.0 if old > 0.5 else 0.0
            err = (old - new) / div
            out[y, x] = new
            for dy, dx, weight in kernel:
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w:
                    out[yy, xx] += err * weight
    return (out > 0.5).astype(np.float32)

def dither_atkinson(img):
    return _diffuse(img, [(0,1,1),(0,2,1),(1,-1,1),(1,0,1),(1,1,1),(2,0,1)], 8.0)

def dither_stucki(img):
    return _diffuse(img, [(0,1,8),(0,2,4),(1,-2,2),(1,-1,4),(1,0,8),(1,1,4),(1,2,2),(2,-2,1),(2,-1,2),(2,0,4),(2,1,2),(2,2,1)], 42.0)

def dither_jjn(img):
    return _diffuse(img, [(0,1,7),(0,2,5),(1,-2,3),(1,-1,5),(1,0,7),(1,1,5),(1,2,3),(2,-2,1),(2,-1,3),(2,0,5),(2,1,3),(2,2,1)], 48.0)

DITHER_MAP = {'Atkinson': dither_atkinson, 'Stucki': dither_stucki, 'JJN': dither_jjn}

def select_best_dither(values, candidates):
    if not candidates:
        raise ValueError('dither_candidates must not be empty')
    small = cv2.resize(values, (max(4, values.shape[1]//4), max(4, values.shape[0]//4)), interpolation=cv2.INTER_AREA)
    best, score = candidates[0], float('inf')
    for name in candidates:
        if name not in DITHER_MAP:
            raise ValueError(f'Unsupported dither method: {name}')
        b = DITHER_MAP[name](small)
        mse = float(np.mean((small - gaussian_filter(b, sigma=0.8)) ** 2))
        if mse < score:
            best, score = name, mse
    return best, DITHER_MAP[best](values)

def correct_over_dense_regions(binary, cfg):
    b = np.asarray(binary, dtype=np.float32).copy()
    density = uniform_filter(b, size=7, mode='reflect')
    over = (density > cfg.max_local_occupancy) & (b > 0)
    if not np.any(over):
        return b
    rng = np.random.default_rng(cfg.seed)
    keep = rng.random(b.shape) < np.clip(cfg.max_local_occupancy / np.maximum(density, 1e-6), 0, 1)
    b[over & ~keep] = 0
    return b
