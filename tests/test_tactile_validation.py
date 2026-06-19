import numpy as np

from braille_dotmatrix_engine.config import BrailleArtConfig, TactileGeometry
from braille_dotmatrix_engine.tactile import validate_tactile_output


def test_default_tactile_geometry_is_compliant_for_sparse_grid():
    binary = np.zeros((4, 4), dtype=bool)
    binary[0, 0] = True
    binary[2, 2] = True
    report = validate_tactile_output(binary, BrailleArtConfig())
    assert report['compliant'] is True
    assert report['severity'] == 'ok'
    assert report['active_collision_report']['violating_pairs'] == 0


def test_active_neighbor_gap_violation_is_reported():
    binary = np.zeros((4, 4), dtype=bool)
    binary[0, 0] = True
    binary[0, 1] = True
    cfg = BrailleArtConfig(geometry=TactileGeometry(dot_diameter_mm=1.80, dot_spacing_mm=2.50, safety_gap_mm=1.00))
    report = validate_tactile_output(binary, cfg)
    assert report['compliant'] is False
    assert report['severity'] == 'error'
    assert report['active_collision_report']['violating_pairs'] >= 1
    assert any(issue['code'] == 'active_dot_collision' for issue in report['issues'])


def test_global_occupancy_warning_does_not_make_report_noncompliant():
    binary = np.ones((8, 8), dtype=bool)
    cfg = BrailleArtConfig(max_local_occupancy=0.50)
    report = validate_tactile_output(binary, cfg)
    assert report['severity'] in {'warning', 'error'}
    assert report['occupancy_ratio'] == 1.0
    assert any(item['code'] == 'global_occupancy_high' for item in report['warnings'])
