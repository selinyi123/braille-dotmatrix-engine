import numpy as np
BRAILLE_BASE = 0x2800

def encode_braille_cell(dots):
    bits = np.asarray(dots, dtype=bool).reshape(8)
    mask = 0
    for i, enabled in enumerate(bits):
        if enabled:
            mask |= 1 << i
    return chr(BRAILLE_BASE + mask)

def decode_braille_cell(ch):
    code = ord(ch) - BRAILLE_BASE
    if len(ch) != 1 or code < 0 or code > 255:
        raise ValueError('not a Unicode Braille pattern')
    return np.array([(code & (1 << i)) != 0 for i in range(8)], dtype=bool)

def unicode_roundtrip_test():
    return all(encode_braille_cell(decode_braille_cell(chr(BRAILLE_BASE + m))) == chr(BRAILLE_BASE + m) for m in range(256))

def encode_to_braille_matrix(dot_binary):
    b = np.asarray(dot_binary, dtype=bool)
    cy, cx = b.shape[0] // 4, b.shape[1] // 2
    out = np.empty((cy, cx), dtype='<U1')
    for r in range(cy):
        for c in range(cx):
            block = b[r*4:r*4+4, c*2:c*2+2]
            out[r, c] = encode_braille_cell([block[0,0], block[1,0], block[2,0], block[3,0], block[0,1], block[1,1], block[2,1], block[3,1]])
    return out

def braille_matrix_to_text(cell_matrix):
    return '\n'.join(''.join(row.tolist()) for row in np.asarray(cell_matrix))
