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


@pytest.mark.parametrize(
    "field,value",
    [
        ("output_width_cells", 80.5),
        ("render_spacing_px", 10.5),
        ("max_output_width_cells", 320.5),
        ("max_total_dots", 2_000_000.5),
        ("clahe_grid_size", 8.5),
        ("tile_size_px", 512.5),
        ("tile_overlap_px", 64.5),
        ("braille_seam_tile", 16.5),
        ("chromatic_cell_w_px", 10.5),
        ("chromatic_cell_h_px", 16.5),
        ("chromatic_luma_threshold", 108.5),
    ],
)
def test_fractional_integer_config_values_are_rejected(field, value):
    cfg = BrailleArtConfig()
    setattr(cfg, field, value)
    with pytest.raises(ValueError, match=field):
        validate_config(cfg)


def test_boolean_integer_config_values_are_rejected():
    cfg = BrailleArtConfig(output_width_cells=True)
    with pytest.raises(ValueError, match="output_width_cells"):
        validate_config(cfg)


def test_output_width_cells_must_not_exceed_configured_limit():
    cfg = BrailleArtConfig(output_width_cells=321, max_output_width_cells=320)
    with pytest.raises(ValueError, match="max_output_width_cells"):
        validate_config(cfg)


def test_max_total_dots_must_be_positive():
    cfg = BrailleArtConfig(max_total_dots=0)
    with pytest.raises(ValueError, match="max_total_dots"):
        validate_config(cfg)
