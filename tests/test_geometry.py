import numpy as np

from braille_dotmatrix_engine import BrailleArtConfig, MaterialProfile, PrinterProfile, TactileGeometry, compensated_dot_radius_mm
from braille_dotmatrix_engine.vector import export_svg


def test_compensated_radius_accounts_for_material_and_printer():
    cfg = BrailleArtConfig(
        geometry=TactileGeometry(dot_diameter_mm=1.0, dot_spacing_mm=3.0, safety_gap_mm=0.6),
        material=MaterialProfile(shrinkage_rate=0.1),
        printer=PrinterProfile(xy_error_mm=0.2),
    )
    expected = min((0.5 / 0.9) + 0.1, (3.0 - 0.6) / 2.0)
    assert compensated_dot_radius_mm(cfg) == expected


def test_svg_uses_compensated_radius(tmp_path):
    cfg = BrailleArtConfig(
        geometry=TactileGeometry(dot_diameter_mm=1.0, dot_spacing_mm=3.0, safety_gap_mm=0.6),
        material=MaterialProfile(shrinkage_rate=0.1),
        printer=PrinterProfile(xy_error_mm=0.2),
    )
    binary = np.ones((4, 2), dtype=bool)
    path = tmp_path / "out.svg"
    report = export_svg(binary, cfg, path)
    radius = compensated_dot_radius_mm(cfg)
    text = path.read_text(encoding="utf-8")
    assert format(radius, ".3f") in text
    assert report["compensated_dot_radius_mm"] == radius
    assert report["geometry"]["radius"]["compensated_dot_radius_mm"] == radius
