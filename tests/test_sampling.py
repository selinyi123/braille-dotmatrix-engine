import pytest

from braille_dotmatrix_engine import BrailleArtConfig
from braille_dotmatrix_engine.sampling import build_dot_grid


def test_build_dot_grid_rejects_invalid_shape():
    cfg = BrailleArtConfig(output_width_cells=4)
    with pytest.raises(ValueError, match="height and width"):
        build_dot_grid(cfg, (32,))
    with pytest.raises(ValueError, match="image height"):
        build_dot_grid(cfg, (0, 32))
    with pytest.raises(ValueError, match="image width"):
        build_dot_grid(cfg, (32, 0))


def test_build_dot_grid_rejects_excessive_total_dots_before_allocation():
    cfg = BrailleArtConfig(output_width_cells=10, max_total_dots=100)
    with pytest.raises(ValueError, match="max_total_dots"):
        build_dot_grid(cfg, (100, 100))


def test_build_dot_grid_rejects_fractional_width_cells_for_direct_api_calls():
    cfg = BrailleArtConfig(output_width_cells=10)
    cfg.output_width_cells = 10.5
    with pytest.raises(ValueError, match="output_width_cells"):
        build_dot_grid(cfg, (32, 32))


def test_build_dot_grid_rejects_fractional_total_dot_limit_for_direct_api_calls():
    cfg = BrailleArtConfig(output_width_cells=4)
    cfg.max_total_dots = 100.5
    with pytest.raises(ValueError, match="max_total_dots"):
        build_dot_grid(cfg, (32, 32))


def test_build_dot_grid_allows_grid_within_total_dot_limit():
    cfg = BrailleArtConfig(output_width_cells=4, max_total_dots=100)
    coords, dx, dy, spacing = build_dot_grid(cfg, (32, 32))
    assert coords.shape == (8, 8, 2)
    assert dx == 8
    assert dy == 8
    assert spacing > 0
