import numpy as np
import pytest

from braille_dotmatrix_engine.braille_unicode import (
    BRAILLE_BASE,
    decode_braille_cell,
    decode_braille_matrix,
    encode_braille_cell,
    encode_to_braille_matrix,
    unicode_roundtrip_test,
)


def test_unicode_roundtrip_all_256_patterns():
    assert unicode_roundtrip_test() is True
    for mask in range(256):
        ch = chr(BRAILLE_BASE + mask)
        assert encode_braille_cell(decode_braille_cell(ch)) == ch


def test_physical_4x2_layout_uses_official_unicode_dot_order():
    cases = {
        (0, 0): 0,
        (1, 0): 1,
        (2, 0): 2,
        (0, 1): 3,
        (1, 1): 4,
        (2, 1): 5,
        (3, 0): 6,
        (3, 1): 7,
    }
    for (row, col), bit in cases.items():
        matrix = np.zeros((4, 2), dtype=bool)
        matrix[row, col] = True
        encoded = encode_to_braille_matrix(matrix)[0, 0]
        assert ord(encoded) == BRAILLE_BASE + (1 << bit)


def test_matrix_encode_decode_roundtrip():
    dot_grid = np.array(
        [
            [True, False, False, True],
            [False, True, True, False],
            [True, True, False, False],
            [False, False, True, True],
            [True, True, True, False],
            [False, True, False, True],
            [True, False, True, False],
            [False, False, False, True],
        ],
        dtype=bool,
    )
    encoded = encode_to_braille_matrix(dot_grid)
    decoded = decode_braille_matrix(encoded)
    assert np.array_equal(dot_grid, decoded)


def test_partial_cells_are_cropped_predictably():
    dot_grid = np.ones((5, 3), dtype=bool)
    encoded = encode_to_braille_matrix(dot_grid)
    decoded = decode_braille_matrix(encoded)
    assert encoded.shape == (1, 1)
    assert decoded.shape == (4, 2)
    assert decoded.all()


def test_decode_braille_matrix_rejects_non_braille_characters():
    with pytest.raises(ValueError, match="non-Braille"):
        decode_braille_matrix(np.array([["A"]]))


def test_decode_braille_matrix_rejects_multi_character_cells():
    with pytest.raises(ValueError, match="non-single-character"):
        decode_braille_matrix(np.array([["⠁⠃"]], dtype=object))
