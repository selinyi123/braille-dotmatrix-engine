from __future__ import annotations

import cv2
import numpy as np


def _as_uint8_image(img) -> np.ndarray:
    arr = np.asarray(img)
    if arr.size == 0 or arr.ndim not in (2, 3):
        raise ValueError("image must be a non-empty 2D grayscale or 3D color array")
    if arr.ndim == 3 and arr.shape[2] not in (3, 4):
        raise ValueError("color image must have 3 or 4 channels")
    if np.issubdtype(arr.dtype, np.floating):
        arr = np.nan_to_num(arr.astype(np.float32), nan=0.0, posinf=255.0, neginf=0.0)
        max_value = float(arr.max()) if arr.size else 0.0
        if max_value <= 1.0:
            arr = arr * 255.0
    return np.clip(arr, 0, 255).astype(np.uint8)


def as_bgr_uint8(img) -> np.ndarray:
    arr = _as_uint8_image(img)
    if arr.ndim == 2:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    if arr.shape[2] == 4:
        return arr[:, :, :3]
    return arr


def float01(img):
    """Convert an image-like array to a finite grayscale float32 image in [0, 1]."""

    bgr = as_bgr_uint8(img)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    return np.clip(np.nan_to_num(gray, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)


def apply_clahe_lab(img_bgr, clip_limit, grid_size):
    bgr = as_bgr_uint8(img_bgr)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
    l2 = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)
