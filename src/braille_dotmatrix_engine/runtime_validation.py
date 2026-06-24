from __future__ import annotations

import math
import numbers
from typing import Any

import numpy as np

__all__ = [
    "as_binary_matrix",
    "as_float32_matrix",
    "require_finite",
    "require_int",
    "require_int_non_negative",
    "require_int_positive",
    "require_unit_interval",
    "validate_image_shape",
]


def require_finite(name: str, value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be finite") from None
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def require_unit_interval(name: str, value: Any) -> float:
    parsed = require_finite(name, value)
    if parsed < 0.0 or parsed > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return parsed


def require_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f"{name} must be an integer")
    return int(value)


def require_int_positive(name: str, value: Any) -> int:
    parsed = require_int(name, value)
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def require_int_non_negative(name: str, value: Any) -> int:
    parsed = require_int(name, value)
    if parsed < 0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def validate_image_shape(shape) -> tuple[int, int]:
    if len(shape) < 2:
        raise ValueError("shape must contain height and width")
    h = require_int_positive("image height", shape[0])
    w = require_int_positive("image width", shape[1])
    return h, w


def as_binary_matrix(binary, cfg=None, *, name: str = "binary") -> np.ndarray:
    b = np.asarray(binary, dtype=bool)
    if b.ndim != 2:
        raise ValueError(f"{name} must be a 2D dot matrix")
    if b.size == 0 or b.shape[0] <= 0 or b.shape[1] <= 0:
        raise ValueError(f"{name} dot matrix must be non-empty")
    if cfg is not None:
        limit = getattr(cfg, "max_total_dots", None)
        if limit is not None:
            max_total = require_int_positive("max_total_dots", limit)
            if b.size > max_total:
                raise ValueError(f"{name} dot matrix too large: {b.size} dots exceeds max_total_dots={max_total}")
    return b


def as_float32_matrix(values, *, name: str = "matrix") -> np.ndarray:
    arr = np.asarray(values, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2D matrix")
    if arr.size == 0 or arr.shape[0] <= 0 or arr.shape[1] <= 0:
        raise ValueError(f"{name} must be non-empty")
    return np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)
