from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class MaterialProfile:
    name: str = "PLA"
    shrinkage_rate: float = 0.02
    hardness_shore: float = 60.0
    manufacturing_tolerance_mm: float = 0.10


@dataclass(frozen=True)
class PrinterProfile:
    type: Literal["FDM", "SLA", "DLP", "MJF", "OTHER"] = "FDM"
    xy_error_mm: float = 0.10
    z_error_mm: float = 0.05


@dataclass(frozen=True)
class TactileGeometry:
    dot_diameter_mm: float = 0.90
    dot_spacing_mm: float = 2.50
    safety_gap_mm: float = 1.00
    dot_height_mm: float = 0.50
    min_dot_diameter_mm: float = 0.80
    min_dot_spacing_mm: float = 2.00

    @property
    def dot_radius_mm(self) -> float:
        return self.dot_diameter_mm / 2.0


@dataclass
class BrailleArtConfig:
    output_width_cells: int = 80
    geometry: TactileGeometry = field(default_factory=TactileGeometry)
    material: MaterialProfile = field(default_factory=MaterialProfile)
    printer: PrinterProfile = field(default_factory=PrinterProfile)
    clahe_clip_limit: float = 2.0
    clahe_grid_size: int = 8
    dither_candidates: list[str] = field(default_factory=lambda: ["Atkinson", "Stucki", "JJN"])
    tile_size_px: int = 512
    tile_overlap_px: int = 64
    seed: int = 42
    mode: Literal["TACTILE", "SCREEN", "CHROMATIC", "ASCII_MONO", "ASCII_COLOR"] = "TACTILE"
    invert_luminance: bool = True
    render_spacing_px: int = 10
    max_local_occupancy: float = 0.72
    strict_tactile_validation: bool = False

    # Mode semantics. ASCII modes use a fast path by default; enable this to
    # attach full Braille/tactile diagnostics to ASCII reports.
    include_braille_diagnostics: bool = False

    # Braille enhancement layer, applied after sampling and before dithering.
    braille_preserve_edges: bool = True
    braille_edge_weight: float = 0.22
    braille_gamma: float = 1.0
    braille_contrast: float = 1.12

    # Braille quality-control layer.
    braille_target_density: float | None = None
    braille_density_strength: float = 0.55
    braille_seam_tile: int = 16
    braille_seam_threshold: float = 0.18

    # ASCII backend configuration.
    ascii_charset: str = " .:-=+*#%@"
    ascii_charset_preset: Literal["custom", "standard", "dense", "blocks", "binary"] = "custom"
    ascii_aspect_ratio: float = 0.50
    ascii_edge_weight: float = 0.25
    ascii_invert: bool = False
    ascii_ansi: bool = False
    ascii_html: bool = False

    # Screen-only chromatic rendering backend.
    chromatic_cell_w_px: int = 10
    chromatic_cell_h_px: int = 16
    chromatic_sigma_ratio: float = 0.62
    chromatic_saturation_boost: float = 1.6
    chromatic_neutral_sat: float = 0.12
    chromatic_contrast: float = 1.35
    chromatic_sharpen: float = 1.10
    chromatic_s_curve: float = 0.25
    chromatic_bloom: float = 0.18
    chromatic_luma_threshold: int = 108
    chromatic_white_balance: bool = True

    @property
    def dot_diameter_mm(self) -> float:
        return self.geometry.dot_diameter_mm

    @property
    def dot_spacing_mm(self) -> float:
        return self.geometry.dot_spacing_mm

    @property
    def dot_radius_mm(self) -> float:
        return self.geometry.dot_radius_mm

    @property
    def safety_gap_mm(self) -> float:
        return self.geometry.safety_gap_mm

    @property
    def min_dot_diameter_mm(self) -> float:
        return self.geometry.min_dot_diameter_mm

    @property
    def min_dot_spacing_mm(self) -> float:
        return self.geometry.min_dot_spacing_mm
