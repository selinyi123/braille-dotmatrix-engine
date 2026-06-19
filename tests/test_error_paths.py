import pytest
from braille_dotmatrix_engine import BrailleArtConfig, process_image
from braille_dotmatrix_engine.dither import select_best_dither

def test_missing_image_path_raises():
    with pytest.raises(FileNotFoundError):
        process_image('missing-input-file.png', BrailleArtConfig())

def test_empty_dither_candidates_raises():
    import numpy as np
    with pytest.raises(ValueError):
        select_best_dither(np.zeros((8, 8), dtype=np.float32), [])
