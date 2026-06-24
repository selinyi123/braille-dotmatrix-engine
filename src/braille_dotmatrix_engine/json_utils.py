from __future__ import annotations

import json
import math
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["to_json_safe", "dumps_json", "write_json"]


def to_json_safe(value: Any) -> Any:
    """Convert common runtime objects into strict-JSON-safe values.

    Python's json module can emit NaN/Infinity by default, but those tokens are
    not valid RFC-compliant JSON. Render and benchmark reports should be safe for
    strict parsers, dashboards, and snapshot contract tests.
    """

    if is_dataclass(value) and not isinstance(value, type):
        return to_json_safe(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return to_json_safe(value.item())
    if isinstance(value, np.ndarray):
        return to_json_safe(value.tolist())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}
    if isinstance(value, set):
        return [to_json_safe(item) for item in sorted(value, key=lambda item: repr(item))]
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    return value


def dumps_json(value: Any, **kwargs) -> str:
    options = {"indent": 2, "ensure_ascii": False, "allow_nan": False}
    options.update(kwargs)
    return json.dumps(to_json_safe(value), **options)


def write_json(value: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps_json(value), encoding="utf-8")
