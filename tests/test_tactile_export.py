import numpy as np
from braille_dotmatrix_engine.config import BrailleArtConfig
from braille_dotmatrix_engine.tactile import binary_to_dot_positions_mm, geometry_report
from braille_dotmatrix_engine.vector import export_svg

def test_geometry_report_is_compliant_by_default():
    report = geometry_report(BrailleArtConfig())
    assert report['compliant'] is True
    assert report['edge_gap_mm'] > 0

def test_binary_to_dot_positions_mm():
    binary = np.zeros((2, 2), dtype=bool)
    binary[0, 1] = True
    positions = binary_to_dot_positions_mm(binary, BrailleArtConfig())
    assert len(positions) == 1
    assert positions[0]['x_mm'] > 0

def test_export_svg_creates_file(tmp_path):
    binary = np.zeros((4, 4), dtype=bool)
    binary[1, 1] = True
    result = export_svg(binary, BrailleArtConfig(), tmp_path / 'out.svg')
    assert result['dot_count'] == 1
    assert (tmp_path / 'out.svg').exists()
    assert '<svg' in (tmp_path / 'out.svg').read_text(encoding='utf-8')
