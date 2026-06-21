from __future__ import annotations

import math
import numbers
from collections.abc import Sequence

from .config import BrailleArtConfig

__all__ = ["VALID_DITHER_METHODS", "VALID_RENDER_MODES", "validate_config"]

VALID_RENDER_MODES = {"TACTILE", "SCREEN", "CHROMATIC", "ASCII_MONO", "ASCII_COLOR"}
VALID_DITHER_METHODS = {"Atkinson", "Stucki", "JJN"}
VALID_ASCII_PRESETS = {"custom", "standard", "dense", "blocks", "binary"}
VALID_PRINTER_TYPES = {"FDM", "SLA", "DLP", "MJF", "OTHER"}


def _finite(name: str, value: float) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def _require_positive(name: str, value: float) -> None:
    if _finite(name, value) <= 0:
        raise ValueError(f"{name} must be positive")


def _require_non_negative(name: str, value: float) -> None:
    if _finite(name, value) < 0:
        raise ValueError(f"{name} must be non-negative")


def _require_unit_interval(name: str, value: float) -> None:
    parsed = _finite(name, value)
    if parsed < 0 or parsed > 1:
        raise ValueError(f"{name} must be between 0 and 1")


def _require_int(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f"{name} must be an integer")
    return int(value)


def _require_int_positive(name: str, value) -> int:
    parsed = _require_int(name, value)
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _require_int_non_negative(name: str, value) -> int:
    parsed = _require_int(name, value)
    if parsed < 0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def _validate_dither_candidates(candidates: Sequence[str]) -> None:
    if not candidates:
        raise ValueError("dither_candidates must not be empty")
    for name in candidates:
        if name not in VALID_DITHER_METHODS:
            raise ValueError(f"Unsupported dither method: {name}")


def validate_config(cfg: BrailleArtConfig) -> None:
    """Validate public configuration values before rendering.

    The dataclass intentionally remains mutable because the CLI applies some
    arguments after construction. This function is the central validation gate
    used by the pipeline and the Python API.
    """

    if str(cfg.mode) not in VALID_RENDER_MODES:
        raise ValueError(f"Unsupported render mode: {cfg.mode}")

    _require_int_positive("output_width_cells", cfg.output_width_cells)
    _require_int_positive("render_spacing_px", cfg.render_spacing_px)
    _require_positive("clahe_clip_limit", float(cfg.clahe_clip_limit))
    _require_int_positive("clahe_grid_size", cfg.clahe_grid_size)

    _validate_dither_candidates(cfg.dither_candidates)

    tile_size = _require_int_positive("tile_size_px", cfg.tile_size_px)
    tile_overlap = _require_int_non_negative("tile_overlap_px", cfg.tile_overlap_px)
    if tile_overlap >= tile_size:
        raise ValueError("tile_overlap_px must be smaller than tile_size_px")

    _require_unit_interval("max_local_occupancy", float(cfg.max_local_occupancy))

    if str(cfg.printer.type) not in VALID_PRINTER_TYPES:
        raise ValueError(f"Unsupported printer type: {cfg.printer.type}")
    _require_non_negative("printer.xy_error_mm", float(cfg.printer.xy_error_mm))
    _require_non_negative("printer.z_error_mm", float(cfg.printer.z_error_mm))

    _require_positive("geometry.dot_diameter_mm", float(cfg.geometry.dot_diameter_mm))
    _require_positive("geometry.dot_spacing_mm", float(cfg.geometry.dot_spacing_mm))
    _require_non_negative("geometry.safety_gap_mm", float(cfg.geometry.safety_gap_mm))
    _require_positive("geometry.dot_height_mm", float(cfg.geometry.dot_height_mm))
    _require_positive("geometry.min_dot_diameter_mm", float(cfg.geometry.min_dot_diameter_mm))
    _require_positive("geometry.min_dot_spacing_mm", float(cfg.geometry.min_dot_spacing_mm))

    _require_non_negative("material.manufacturing_tolerance_mm", float(cfg.material.manufacturing_tolerance_mm))
    _require_non_negative("material.hardness_shore", float(cfg.material.hardness_shore))
    shrinkage = _finite("material.shrinkage_rate", float(cfg.material.shrinkage_rate))
    if shrinkage < 0 or shrinkage >= 1:
        raise ValueError("material.shrinkage_rate must be in [0, 1)")

    _require_unit_interval("braille_edge_weight", float(cfg.braille_edge_weight))
    _require_positive("braille_gamma", float(cfg.braille_gamma))
    _require_positive("braille_contrast", float(cfg.braille_contrast))
    if cfg.braille_target_density is not None:
        _require_unit_interval("braille_target_density", float(cfg.braille_target_density))
    _require_unit_interval("braille_density_strength", float(cfg.braille_density_strength))
    _require_int_positive("braille_seam_tile", cfg.braille_seam_tile)
    _require_unit_interval("braille_seam_threshold", float(cfg.braille_seam_threshold))

    if str(cfg.ascii_charset_preset) not in VALID_ASCII_PRESETS:
        raise ValueError(f"Unsupported ascii charset preset: {cfg.ascii_charset_preset}")
    _require_positive("ascii_aspect_ratio", float(cfg.ascii_aspect_ratio))
    if not str(cfg.ascii_charset):
        raise ValueError("ascii_charset must not be empty")
    _require_unit_interval("ascii_edge_weight", float(cfg.ascii_edge_weight))

    _require_int_positive("chromatic_cell_w_px", cfg.chromatic_cell_w_px)
    _require_int_positive("chromatic_cell_h_px", cfg.chromatic_cell_h_px)
    _require_positive("chromatic_sigma_ratio", float(cfg.chromatic_sigma_ratio))
    _require_non_negative("chromatic_saturation_boost", float(cfg.chromatic_saturation_boost))
    _require_unit_interval("chromatic_neutral_sat", float(cfg.chromatic_neutral_sat))
    _require_positive("chromatic_contrast", float(cfg.chromatic_contrast))
    _require_non_negative("chromatic_sharpen", float(cfg.chromatic_sharpen))
    _finite("chromatic_s_curve", float(cfg.chromatic_s_curve))
    _require_non_negative("chromatic_bloom", float(cfg.chromatic_bloom))
    chromatic_luma_threshold = _require_int_non_negative("chromatic_luma_threshold", cfg.chromatic_luma_threshold)
    if chromatic_luma_threshold > 255:
        raise ValueError("chromatic_luma_threshold must be between 0 and 255")
