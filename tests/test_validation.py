import pytest

from braille_dotmatrix_engine import BrailleArtConfig, MaterialProfile, TactileGeometry, validate_config


def test_invalid_render_mode_rejected():
    cfg = BrailleArtConfig(mode="INVALID")
    with pytest.raises(ValueError, match="Unsupported render mode"):
        validate_config(cfg)


def test_invalid_dither_candidate_rejected():
    cfg = BrailleArtConfig(dither_candidates=["Atkinson", "Unknown"])
    with pytest.raises(ValueError, match="Unsupported dither method"):
        validate_config(cfg)


def test_invalid_geometry_rejected():
    cfg = BrailleArtConfig(geometry=TactileGeometry(dot_diameter_mm=0.0))
    with pytest.raises(ValueError, match="geometry.dot_diameter_mm"):
        validate_config(cfg)


def test_invalid_material_shrinkage_rejected():
    cfg = BrailleArtConfig(material=MaterialProfile(shrinkage_rate=1.0))
    with pytest.raises(ValueError, match="material.shrinkage_rate"):
        validate_config(cfg)


def test_invalid_chromatic_parameters_rejected():
    cfg = BrailleArtConfig(chromatic_sigma_ratio=0.0)
    with pytest.raises(ValueError, match="chromatic_sigma_ratio"):
        validate_config(cfg)
