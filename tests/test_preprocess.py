import numpy as np
import pytest

from braille_dotmatrix_engine.preprocess import apply_clahe_lab, as_bgr_uint8, float01


def test_float01_converts_bgr_to_2d_grayscale_float():
    image = np.zeros((8, 8, 3), dtype=np.uint8)
    image[:, :, 1] = 255
    out = float01(image)
    assert out.shape == (8, 8)
    assert out.dtype == np.float32
    assert 0.0 <= float(out.min()) <= float(out.max()) <= 1.0


def test_as_bgr_uint8_scales_unit_float_images():
    image = np.ones((4, 4, 3), dtype=np.float32)
    out = as_bgr_uint8(image)
    assert out.dtype == np.uint8
    assert int(out.max()) == 255


def test_preprocess_rejects_empty_image():
    with pytest.raises(ValueError, match="non-empty"):
        float01(np.zeros((0, 8, 3), dtype=np.uint8))


def test_preprocess_rejects_invalid_channel_count():
    with pytest.raises(ValueError, match="3 or 4 channels"):
        as_bgr_uint8(np.zeros((8, 8, 2), dtype=np.uint8))


def test_apply_clahe_lab_accepts_grayscale_input():
    image = np.zeros((8, 8), dtype=np.uint8)
    out = apply_clahe_lab(image, 2.0, 8)
    assert out.shape == (8, 8, 3)
    assert out.dtype == np.uint8
