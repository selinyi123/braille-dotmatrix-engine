from __future__ import annotations

import numbers
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from .preprocess import as_bgr_uint8

__all__ = ["build_chromatic_array", "render_chromatic_png"]


def _require_int_positive(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f"{name} must be an integer")
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _as_rgb_float(source_bgr: np.ndarray) -> np.ndarray:
    bgr = as_bgr_uint8(source_bgr)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)


def _white_balance_highlights(rgb: np.ndarray) -> np.ndarray:
    luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    threshold = np.percentile(luma, 90)
    mask = luma >= threshold
    if int(mask.sum()) < 16:
        return rgb
    means = np.array([rgb[:, :, i][mask].mean() for i in range(3)], dtype=np.float32)
    target = float(means.mean())
    gains = target / np.maximum(means, 1e-6)
    return np.clip(rgb * gains[None, None, :], 0, 255).astype(np.float32)


def _enhance_source(rgb: np.ndarray, cfg) -> np.ndarray:
    out = rgb.astype(np.float32)
    if getattr(cfg, "chromatic_white_balance", True):
        out = _white_balance_highlights(out)
    contrast = float(getattr(cfg, "chromatic_contrast", 1.0))
    out = np.clip((out - 128.0) * contrast + 128.0, 0, 255)
    sharpen = float(getattr(cfg, "chromatic_sharpen", 0.0))
    if sharpen > 1.0:
        blur = gaussian_filter(out, sigma=(1.0, 1.0, 0.0))
        out = np.clip(out + (out - blur) * (sharpen - 1.0), 0, 255)
    strength = float(getattr(cfg, "chromatic_s_curve", 0.0))
    if strength:
        x = np.clip(out / 255.0, 0, 1)
        out = np.clip(x + strength * 4.0 * x * (1.0 - x) * (x - 0.5), 0, 1) * 255.0
    return out.astype(np.float32)


def _neutral_aware_saturation(colors: np.ndarray, cfg) -> np.ndarray:
    c = np.clip(colors.astype(np.float32) / 255.0, 0, 1)
    cmax = c.max(axis=1)
    cmin = c.min(axis=1)
    delta = cmax - cmin
    sat = np.where(cmax > 1e-6, delta / np.maximum(cmax, 1e-6), 0.0)
    luma = 0.299 * c[:, 0] + 0.587 * c[:, 1] + 0.114 * c[:, 2]
    neutral = np.stack([luma, luma, luma], axis=-1)
    boost = float(getattr(cfg, "chromatic_saturation_boost", 1.0))
    neutral_sat = float(getattr(cfg, "chromatic_neutral_sat", 0.12))
    chroma = luma[:, None] + (c - luma[:, None]) * boost
    alpha = np.clip((sat - neutral_sat) / 0.18, 0.0, 1.0)[:, None]
    out = (1.0 - alpha) * neutral + alpha * chroma
    return np.clip(out * 255.0, 0, 255).astype(np.float32)


def build_chromatic_array(binary, source_bgr, cfg) -> np.ndarray:
    b = np.asarray(binary, dtype=bool)
    if b.ndim != 2:
        raise ValueError("binary must be a 2D dot matrix")
    dot_h, dot_w = b.shape
    if dot_h < 4 or dot_w < 2:
        return np.zeros((1, 1, 3), dtype=np.uint8)

    cell_w = _require_int_positive("chromatic_cell_w_px", getattr(cfg, "chromatic_cell_w_px", 10))
    cell_h = _require_int_positive("chromatic_cell_h_px", getattr(cfg, "chromatic_cell_h_px", 16))
    rows = dot_h // 4
    cols = dot_w // 2
    out_h = max(1, rows * cell_h)
    out_w = max(1, cols * cell_w)

    src = _enhance_source(_as_rgb_float(source_bgr), cfg)
    src = cv2.resize(src, (dot_w, dot_h), interpolation=cv2.INTER_AREA)
    luma = 0.299 * src[:, :, 0] + 0.587 * src[:, :, 1] + 0.114 * src[:, :, 2]
    threshold = float(getattr(cfg, "chromatic_luma_threshold", 108))

    impulses = np.zeros((out_h, out_w, 3), dtype=np.float32)
    weights = np.zeros((out_h, out_w), dtype=np.float32)
    cx_frac = (0.25, 0.75)

    for r in range(4):
        for c in range(2):
            active = b[r::4, c::2][:rows, :cols] & (luma[r::4, c::2][:rows, :cols] >= threshold)
            yy, xx = np.where(active)
            if yy.size == 0:
                continue
            px = np.clip((xx * cell_w + cx_frac[c] * cell_w).astype(np.int64), 0, out_w - 1)
            py = np.clip((yy * cell_h + (0.125 + r * 0.25) * cell_h).astype(np.int64), 0, out_h - 1)
            colors = _neutral_aware_saturation(src[r::4, c::2][:rows, :cols][yy, xx], cfg)
            np.add.at(impulses, (py, px, slice(None)), colors)
            np.add.at(weights, (py, px), 1.0)

    sigma = max(float(getattr(cfg, "chromatic_sigma_ratio", 0.62)) * (cell_w / 2.0), 0.35)
    blurred = gaussian_filter(impulses, sigma=(sigma, sigma, 0.0))
    wblur = gaussian_filter(weights, sigma=sigma)
    out = blurred / np.maximum(wblur[:, :, None], 1e-6)
    out *= np.clip(wblur[:, :, None] / max(float(wblur.max()), 1e-6), 0, 1)

    bloom = float(getattr(cfg, "chromatic_bloom", 0.18))
    if bloom > 0:
        bright = np.clip(out - 160.0, 0, 255)
        out = np.clip(out + gaussian_filter(bright, sigma=(3, 3, 0)) * bloom, 0, 255)
    return np.clip(out, 0, 255).astype(np.uint8)


def render_chromatic_png(binary, source_bgr, cfg, path) -> dict:
    arr = build_chromatic_array(binary, source_bgr, cfg)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, mode="RGB").save(Path(path))
    return {
        "backend": "CHROMATIC",
        "shape": [int(arr.shape[0]), int(arr.shape[1]), int(arr.shape[2])],
        "cell_w_px": _require_int_positive("chromatic_cell_w_px", getattr(cfg, "chromatic_cell_w_px", 10)),
        "cell_h_px": _require_int_positive("chromatic_cell_h_px", getattr(cfg, "chromatic_cell_h_px", 16)),
        "sigma_ratio": float(getattr(cfg, "chromatic_sigma_ratio", 0.62)),
    }
