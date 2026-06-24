import numpy as np
import pytest

from braille_dotmatrix_engine import BrailleArtConfig
from braille_dotmatrix_engine.tactile import binary_to_dot_positions_mm, validate_tactile_output


def test_tactile_output_rejects_non_2d_binary_matrix():
    cfg = BrailleArtConfig()
    with pytest.raises(ValueError, match='2D dot matrix'):
        validate_tactile_output(np.zeros((4,), dtype=bool), cfg)


def test_tactile_positions_rejects_non_2d_binary_matrix():
    cfg = BrailleArtConfig()
    with pytest.raises(ValueError, match='2D dot matrix'):
        binary_to_dot_positions_mm(np.zeros((4,), dtype=bool), cfg)


def test_tactile_output_rejects_oversized_matrix():
    cfg = BrailleArtConfig(max_total_dots=4)
    with pytest.raises(ValueError, match='max_total_dots'):
        validate_tactile_output(np.zeros((3, 3), dtype=bool), cfg)


def test_tactile_output_accepts_valid_matrix():
    cfg = BrailleArtConfig()
    binary = np.zeros((4, 4), dtype=bool)
    report = validate_tactile_output(binary, cfg)
    assert report['dot_count'] == 0
    assert report['occupancy_ratio'] == 0.0
    assert report['active_collision_report']['violating_pairs'] == 0
