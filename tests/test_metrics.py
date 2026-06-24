import numpy as np
import pytest

from braille_dotmatrix_engine.config import BrailleArtConfig
from braille_dotmatrix_engine.metrics import compute_quality_metrics, edge_score, local_density_over, mse, occupancy, psnr


def test_basic_metrics_are_finite():
    a = np.zeros((8, 8), dtype=np.float32)
    b = np.zeros((8, 8), dtype=np.float32)
    assert mse(a, b) == 0.0
    assert psnr(a, b) == float('inf')


def test_occupancy_counts_active_dots():
    b = np.zeros((4, 4), dtype=bool)
    b[0, 0] = True
    result = occupancy(b)
    assert result['active'] == 1
    assert result['total'] == 16


def test_metrics_reject_non_2d_direct_api_inputs():
    with pytest.raises(ValueError, match='2D'):
        mse(np.zeros((4,), dtype=np.float32), np.zeros((4,), dtype=np.float32))
    with pytest.raises(ValueError, match='2D dot matrix'):
        occupancy(np.zeros((4,), dtype=bool))
    with pytest.raises(ValueError, match='2D dot matrix'):
        local_density_over(np.zeros((4,), dtype=bool), 0.5)


def test_quality_metrics_report_keys():
    values = np.linspace(0, 1, 64, dtype=np.float32).reshape(8, 8)
    binary = values > 0.5
    result = compute_quality_metrics(values, binary, BrailleArtConfig())
    assert 'mse' in result
    assert 'psnr' in result
    assert 'edge_score' in result
    assert 'occupancy' in result
    assert 0.0 <= edge_score(values, binary) <= 1.0
