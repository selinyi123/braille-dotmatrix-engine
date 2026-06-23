import numpy as np
import pytest

from braille_dotmatrix_engine import BrailleArtConfig
from braille_dotmatrix_engine.raster import render_tactile_png
from braille_dotmatrix_engine.vector import export_svg


def test_raster_rejects_non_2d_binary_matrix(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4)
    with pytest.raises(ValueError, match='2D dot matrix'):
        render_tactile_png(np.zeros((4,), dtype=bool), cfg, tmp_path / 'out.png')


def test_raster_rejects_oversized_binary_matrix(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4, max_total_dots=10)
    with pytest.raises(ValueError, match='max_total_dots'):
        render_tactile_png(np.ones((4, 4), dtype=bool), cfg, tmp_path / 'out.png')


def test_raster_creates_parent_directory(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4)
    path = tmp_path / 'nested' / 'out.png'
    render_tactile_png(np.zeros((4, 4), dtype=bool), cfg, path)
    assert path.exists()


def test_vector_rejects_non_2d_binary_matrix(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4)
    with pytest.raises(ValueError, match='2D dot matrix'):
        export_svg(np.zeros((4,), dtype=bool), cfg, tmp_path / 'out.svg')


def test_vector_rejects_oversized_binary_matrix(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4, max_total_dots=10)
    with pytest.raises(ValueError, match='max_total_dots'):
        export_svg(np.ones((4, 4), dtype=bool), cfg, tmp_path / 'out.svg')


def test_vector_creates_parent_directory(tmp_path):
    cfg = BrailleArtConfig(output_width_cells=4)
    path = tmp_path / 'nested' / 'out.svg'
    report = export_svg(np.zeros((4, 4), dtype=bool), cfg, path)
    assert path.exists()
    assert report['path'].endswith('out.svg')
