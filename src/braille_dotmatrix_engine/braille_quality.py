from __future__ import annotations

import numpy as np

__all__ = ["apply_density_control", "analyze_braille_quality"]


def _clamp01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def apply_density_control(values, cfg) -> tuple[np.ndarray, dict]:
    """Adjust sampled values toward a target dot density before dithering.

    The controller is deliberately conservative: it shifts the value field
    around the 0.5 dither threshold instead of rewriting the dither algorithm.
    """

    arr = np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)
    target = getattr(cfg, "braille_target_density", None)
    estimated_density = float(np.mean(arr > 0.5)) if arr.size else 0.0
    report = {
        "enabled": target is not None,
        "target_density": None if target is None else _clamp01(float(target)),
        "estimated_density_before": estimated_density,
        "strength": float(getattr(cfg, "braille_density_strength", 0.55)),
        "threshold_shift": 0.0,
    }
    if target is None or arr.size == 0:
        return arr, report

    target_density = _clamp01(float(target))
    if target_density <= 0.0 or target_density >= 1.0:
        desired_threshold = 1.0 - target_density
    else:
        desired_threshold = float(np.quantile(arr, 1.0 - target_density))
    strength = float(np.clip(getattr(cfg, "braille_density_strength", 0.55), 0.0, 1.0))
    shift = (0.5 - desired_threshold) * strength
    adjusted = np.clip(arr + shift, 0.0, 1.0).astype(np.float32)
    report.update({
        "estimated_density_after": float(np.mean(adjusted > 0.5)),
        "threshold_shift": float(shift),
        "desired_threshold": float(desired_threshold),
    })
    return adjusted, report


def _tile_means(binary: np.ndarray, tile: int) -> np.ndarray:
    b = np.asarray(binary, dtype=np.float32)
    tile = max(2, int(tile))
    rows = max(1, int(np.ceil(b.shape[0] / tile)))
    cols = max(1, int(np.ceil(b.shape[1] / tile)))
    out = np.zeros((rows, cols), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            part = b[r * tile:(r + 1) * tile, c * tile:(c + 1) * tile]
            out[r, c] = float(part.mean()) if part.size else 0.0
    return out


def analyze_braille_quality(binary, cfg) -> dict:
    b = np.asarray(binary, dtype=bool)
    density = float(b.mean()) if b.size else 0.0
    tile = int(getattr(cfg, "braille_seam_tile", 16))
    means = _tile_means(b, tile)
    horizontal = np.abs(np.diff(means, axis=1)) if means.shape[1] > 1 else np.array([], dtype=np.float32)
    vertical = np.abs(np.diff(means, axis=0)) if means.shape[0] > 1 else np.array([], dtype=np.float32)
    seam_values = np.concatenate([horizontal.ravel(), vertical.ravel()]) if horizontal.size or vertical.size else np.array([0.0], dtype=np.float32)
    seam_score = float(seam_values.mean())
    threshold = float(getattr(cfg, "braille_seam_threshold", 0.18))
    target = getattr(cfg, "braille_target_density", None)
    density_error = None if target is None else abs(density - _clamp01(float(target)))
    return {
        "dot_density": density,
        "target_density": None if target is None else _clamp01(float(target)),
        "density_error": density_error,
        "tile_size": tile,
        "tile_rows": int(means.shape[0]),
        "tile_cols": int(means.shape[1]),
        "seam_score": seam_score,
        "seam_threshold": threshold,
        "seam_warning": bool(seam_score > threshold),
    }
