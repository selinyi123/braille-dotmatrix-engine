import numpy as np

from braille_dotmatrix_engine import BrailleArtConfig, enhance_sampled_values


def test_enhance_sampled_values_keeps_shape_and_range():
    values = np.linspace(0, 1, 64, dtype=np.float32).reshape(8, 8)
    cfg = BrailleArtConfig(braille_edge_weight=0.2, braille_contrast=1.1)
    enhanced = enhance_sampled_values(values, cfg)
    assert enhanced.shape == values.shape
    assert enhanced.dtype == np.float32
    assert float(enhanced.min()) >= 0.0
    assert float(enhanced.max()) <= 1.0


def test_enhance_sampled_values_is_deterministic():
    values = np.eye(8, dtype=np.float32)
    cfg = BrailleArtConfig(braille_edge_weight=0.4, braille_gamma=0.9)
    a = enhance_sampled_values(values, cfg)
    b = enhance_sampled_values(values, cfg)
    assert np.array_equal(a, b)
