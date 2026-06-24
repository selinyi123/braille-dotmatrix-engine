import numpy as np
import pytest

from braille_dotmatrix_engine import BrailleArtConfig
from braille_dotmatrix_engine.chromatic import build_chromatic_array
from braille_dotmatrix_engine.metrics import edge_score, occupancy
from braille_dotmatrix_engine.tactile import binary_to_dot_positions_mm, validate_tactile_output


def test_tactile_direct_apis_reject_non_2d_binary():
    cfg = BrailleArtConfig(output_width_cells=4)
    with pytest.raises(ValueError, match='2D dot matrix'):
        validate_tactile_output(np.zeros((4,), dtype=bool), cfg)
    with pytest.raises(ValueError, match='2D dot matrix'):
        binary_to_dot_positions_mm(np.zeros((4,), dtype=bool), cfg)


def test_tactile_direct_apis_reject_oversized_binary():
    cfg = BrailleArtConfig(output_width_cells=4, max_total_dots=10)
    with pytest.raises(ValueError, match='max_total_dots'):
        validate_tactile_output(np.ones((4, 4), dtype=bool), cfg)


def test_metrics_direct_apis_reject_invalid_shapes():
    with pytest.raises(ValueError, match='2D'):
        occupancy(np.zeros((4,), dtype=bool))
    with pytest.raises(ValueError, match='2D'):
        edge_score(np.zeros((4,), dtype=np.float32), np.zeros((4,), dtype=bool))


def test_chromatic_validates_source_even_for_tiny_binary():
    cfg = BrailleArtConfig(output_width_cells=4)
    tiny = np.zeros((2, 2), dtype=bool)
    with pytest.raises(ValueError, match='image'):
        build_chromatic_array(tiny, np.zeros((0, 0, 3), dtype=np.uint8), cfg)
