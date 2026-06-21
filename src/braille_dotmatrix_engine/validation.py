from __future__ import annotations

from .config import BrailleArtConfig

__all__ = ["validate_config"]


def _require_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_unit_interval(name: str, value: float) -> None:
    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1")


def validate_config(cfg: BrailleArtConfig) -> None:
    """Validate public configuration values before rendering.

    The dataclass intentionally remains mutable because the CLI applies some
    arguments after construction. This function is the central validation gate
    used by the pipeline.
    """

    _require_positive("output_width_cells", int(cfg.output_width_cells))
    _require_positive("render_spacing_px", int(cfg.render_spacing_px))
    _require_positive("clahe_grid_size", int(cfg.clahe_grid_size))
    _require_positive("tile_size_px", int(cfg.tile_size_px))
    if int(cfg.tile_overlap_px) < 0:
        raise ValueError("tile_overlap_px must be non-negative")
    if int(cfg.tile_overlap_px) >= int(cfg.tile_size_px):
        raise ValueError("tile_overlap_px must be smaller than tile_size_px")

    _require_positive("ascii_aspect_ratio", float(cfg.ascii_aspect_ratio))
    if not str(cfg.ascii_charset):
        raise ValueError("ascii_charset must not be empty")
    _require_unit_interval("ascii_edge_weight", float(cfg.ascii_edge_weight))

    if cfg.braille_target_density is not None:
        _require_unit_interval("braille_target_density", float(cfg.braille_target_density))
    _require_unit_interval("braille_density_strength", float(cfg.braille_density_strength))
    if int(cfg.braille_seam_tile) <= 0:
        raise ValueError("braille_seam_tile must be positive")
    _require_unit_interval("braille_seam_threshold", float(cfg.braille_seam_threshold))

    if int(cfg.chromatic_luma_threshold) < 0 or int(cfg.chromatic_luma_threshold) > 255:
        raise ValueError("chromatic_luma_threshold must be between 0 and 255")
    _require_positive("chromatic_cell_w_px", int(cfg.chromatic_cell_w_px))
    _require_positive("chromatic_cell_h_px", int(cfg.chromatic_cell_h_px))
