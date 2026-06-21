from __future__ import annotations

import numpy as np

BRAILLE_BASE = 0x2800
BRAILLE_MAX = 0x28FF

# Unicode Braille uses the physical 2x4 dot layout below:
#
#   1 4
#   2 5
#   3 6
#   7 8
#
# The corresponding bit positions are:
#
#   bit0 bit3
#   bit1 bit4
#   bit2 bit5
#   bit6 bit7
#
# This table maps matrix[row, col] -> Unicode bit index.
BRAILLE_BIT_LAYOUT = np.array(
    [
        [0, 3],
        [1, 4],
        [2, 5],
        [6, 7],
    ],
    dtype=np.uint8,
)

BRAILLE_WEIGHTS = (1 << BRAILLE_BIT_LAYOUT).astype(np.uint16)


def _as_8_dot_vector(dots) -> np.ndarray:
    """Normalize an arbitrary 8-dot iterable into a flat boolean vector.

    The public scalar encoder keeps the conventional logical order:
    dot1, dot2, dot3, dot4, dot5, dot6, dot7, dot8.
    """

    bits = np.asarray(dots, dtype=bool).reshape(8)
    return bits


def encode_braille_cell(dots) -> str:
    """Encode one logical 8-dot Braille cell into Unicode U+2800..U+28FF."""

    bits = _as_8_dot_vector(dots)
    powers = (1 << np.arange(8, dtype=np.uint16)).astype(np.uint16)
    mask = int(np.sum(bits.astype(np.uint16) * powers, dtype=np.uint16))
    return chr(BRAILLE_BASE + mask)


def decode_braille_cell(ch: str) -> np.ndarray:
    """Decode one Unicode Braille character into logical dot order 1..8."""

    if len(ch) != 1:
        raise ValueError("expected exactly one Unicode Braille character")
    code = ord(ch) - BRAILLE_BASE
    if code < 0 or code > 255:
        raise ValueError("not a Unicode Braille pattern")
    powers = (1 << np.arange(8, dtype=np.uint16)).astype(np.uint16)
    return ((np.uint16(code) & powers) != 0).astype(bool)


def unicode_roundtrip_test() -> bool:
    """Exhaustively validate all 256 Unicode Braille patterns."""

    codes = np.arange(256, dtype=np.uint16)
    powers = (1 << np.arange(8, dtype=np.uint16)).astype(np.uint16)
    decoded = (codes[:, None] & powers[None, :]) != 0
    reencoded = np.sum(decoded.astype(np.uint16) * powers[None, :], axis=1, dtype=np.uint16)
    return bool(np.array_equal(codes, reencoded))


def encode_to_braille_matrix(dot_binary) -> np.ndarray:
    """Encode a 2D binary dot grid into a matrix of Unicode Braille characters.

    Input shape is interpreted as physical dot rows and columns. Every 4x2
    physical block becomes one Unicode Braille cell using the official 8-dot
    bit layout. Extra incomplete rows/columns are intentionally cropped because
    a Unicode Braille cell cannot represent partial 4x2 geometry.
    """

    b = np.asarray(dot_binary, dtype=bool)
    if b.ndim != 2:
        raise ValueError("dot_binary must be a 2D array")

    cy, cx = b.shape[0] // 4, b.shape[1] // 2
    if cy == 0 or cx == 0:
        return np.empty((cy, cx), dtype="<U1")

    cropped = b[: cy * 4, : cx * 2]
    blocks = cropped.reshape(cy, 4, cx, 2).transpose(0, 2, 1, 3)
    masks = np.sum(blocks.astype(np.uint16) * BRAILLE_WEIGHTS[None, None, :, :], axis=(2, 3), dtype=np.uint16)
    encoder = np.frompyfunc(lambda value: chr(BRAILLE_BASE + int(value)), 1, 1)
    return encoder(masks).astype("<U1")


def _decode_matrix_cell_to_mask(ch) -> int:
    text = str(ch)
    if len(text) != 1:
        raise ValueError("cell_matrix contains non-single-character cells")
    codepoint = ord(text)
    if codepoint < BRAILLE_BASE or codepoint > BRAILLE_MAX:
        raise ValueError("cell_matrix contains non-Braille characters")
    return codepoint - BRAILLE_BASE


def decode_braille_matrix(cell_matrix) -> np.ndarray:
    """Decode a Unicode Braille matrix back into a physical 4x2 dot grid."""

    cells = np.asarray(cell_matrix)
    if cells.ndim == 0:
        cells = cells.reshape(1, 1)
    if cells.ndim != 2:
        raise ValueError("cell_matrix must be a 2D array")

    decode = np.frompyfunc(_decode_matrix_cell_to_mask, 1, 1)
    masks = decode(cells).astype(np.uint16)

    blocks = (masks[:, :, None, None] & BRAILLE_WEIGHTS[None, None, :, :]) != 0
    return blocks.transpose(0, 2, 1, 3).reshape(cells.shape[0] * 4, cells.shape[1] * 2)


def braille_matrix_to_text(cell_matrix) -> str:
    """Serialize a Unicode Braille matrix as newline-separated text."""

    return "\n".join("".join(row.tolist()) for row in np.asarray(cell_matrix))
