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
    mode: Literal["TACTILE", "SCREEN"] = "TACTILE"
    invert_luminance: bool = True
    render_spacing_px: int = 10
    max_local_occupancy: float = 0.72
    strict_tactile_validation: bool = False

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
