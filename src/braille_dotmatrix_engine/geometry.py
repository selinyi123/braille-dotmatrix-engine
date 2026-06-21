from __future__ import annotations

from typing import Any


def compensated_dot_radius_mm(cfg: Any) -> float:
    """Return the manufacturing-compensated dot radius in millimeters."""
    raw_radius = float(cfg.dot_radius_mm)
    shrinkage_rate = float(getattr(cfg.material, "shrinkage_rate", 0.0))
    xy_error_mm = float(getattr(cfg.printer, "xy_error_mm", 0.0))
    spacing_mm = float(cfg.dot_spacing_mm)
    safety_gap_mm = float(cfg.safety_gap_mm)

    compensated = raw_radius / max(1.0 - shrinkage_rate, 1e-6)
    compensated += xy_error_mm * 0.5
    max_radius = max((spacing_mm - safety_gap_mm) / 2.0, 0.0)
    return float(min(compensated, max_radius))


def dot_radius_report(cfg: Any) -> dict:
    """Return raw and compensated radius diagnostics."""
    return {
        "raw_dot_radius_mm": float(cfg.dot_radius_mm),
        "compensated_dot_radius_mm": compensated_dot_radius_mm(cfg),
        "shrinkage_rate": float(getattr(cfg.material, "shrinkage_rate", 0.0)),
        "printer_xy_error_mm": float(getattr(cfg.printer, "xy_error_mm", 0.0)),
    }
