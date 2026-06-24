from __future__ import annotations

import math

import cv2
import numpy as np
from scipy.ndimage import sobel, uniform_filter

from .runtime_validation import as_binary_matrix, as_float32_matrix


def _same_shape(reference, estimate):
    a = as_float32_matrix(reference, name='reference')
    b = as_float32_matrix(estimate, name='estimate')
    if a.shape != b.shape:
        b = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
    return a, b


def mse(reference, estimate) -> float:
    a, b = _same_shape(reference, estimate)
    return float(np.mean((a - b) ** 2))


def psnr(reference, estimate, max_value: float = 1.0) -> float:
    err = mse(reference, estimate)
    if err <= 1e-12:
        return float('inf')
    return float(20.0 * math.log10(max_value) - 10.0 * math.log10(err))


def occupancy(binary) -> dict:
    b = as_binary_matrix(binary)
    active = int(np.count_nonzero(b))
    total = int(b.size)
    return {'active': active, 'total': total, 'ratio': float(active / total)}


def edge_score(values, binary) -> float:
    v, b = _same_shape(values, binary)
    ev = np.hypot(sobel(v, axis=0), sobel(v, axis=1))
    eb = np.hypot(sobel(b, axis=0), sobel(b, axis=1))
    ev = ev / max(float(ev.max()), 1e-6)
    eb = eb / max(float(eb.max()), 1e-6)
    return float(1.0 - np.mean(np.abs(ev - eb)))


def local_density_over(binary, limit: float) -> float:
    b = as_float32_matrix(as_binary_matrix(binary), name='binary')
    density = uniform_filter(b, size=7, mode='reflect')
    return float(np.mean(density > float(limit)))


def compute_quality_metrics(values, binary, cfg) -> dict:
    b = as_float32_matrix(as_binary_matrix(binary, cfg), name='binary')
    reconstructed = cv2.GaussianBlur(b, (0, 0), sigmaX=0.8, sigmaY=0.8)
    return {
        'mse': mse(values, reconstructed),
        'psnr': psnr(values, reconstructed),
        'edge_score': edge_score(values, b),
        'occupancy': occupancy(binary),
        'local_density_over_limit': local_density_over(binary, cfg.max_local_occupancy),
    }
