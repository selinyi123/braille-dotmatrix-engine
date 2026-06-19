from __future__ import annotations

import cv2
import numpy as np

__all__ = ["enhance_sampled_values"]


def _normalize01(arr: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.float32)
    lo = float(np.min(a)) if a.size else 0.0
    hi = float(np.max(a)) if a.size else 1.0
    if hi - lo < 1e-6:
        return np.clip(a, 0.0, 1.0)
    return np.clip((a - lo) / (hi - lo), 0.0, 1.0)


def enhance_sampled_values(values, cfg) -> np.ndarray:
    """Enhance sampled dot luminance before error diffusion.

    The function is intentionally small and deterministic. It strengthens
    structure for Braille output without changing the official Unicode Braille
    encoding layer.
    """

    v = np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)

    gamma = float(getattr(cfg, "braille_gamma", 1.0))
    if gamma > 0 and abs(gamma - 1.0) > 1e-6:
        v = np.power(v, gamma).astype(np.float32)

    contrast = float(getattr(cfg, "braille_contrast", 1.0))
    if abs(contrast - 1.0) > 1e-6:
        v = np.clip((v - 0.5) * contrast + 0.5, 0.0, 1.0)

    if bool(getattr(cfg, "braille_preserve_edges", True)):
        edge_weight = float(getattr(cfg, "braille_edge_weight", 0.0))
        if edge_weight > 0 and min(v.shape) >= 3:
            gx = cv2.Sobel(v, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(v, cv2.CV_32F, 0, 1, ksize=3)
            edges = _normalize01(np.sqrt(gx * gx + gy * gy))
            v = np.clip(v + edges * edge_weight, 0.0, 1.0)

    return v.astype(np.float32)
