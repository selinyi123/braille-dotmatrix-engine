import pytest

from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image, validate_config


def test_validate_config_accepts_default():
    validate_config(BrailleArtConfig())


def test_validate_config_rejects_bad_ascii_aspect():
    cfg = BrailleArtConfig(ascii_aspect_ratio=0)
    with pytest.raises(ValueError, match='ascii_aspect_ratio'):
        validate_config(cfg)


def test_process_image_validates_config_before_render(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=64)
    cfg = BrailleArtConfig(output_width_cells=0)
    with pytest.raises(ValueError, match='output_width_cells'):
        process_image(image, cfg, tmp_path / 'out.png', tmp_path / 'out.txt', tmp_path / 'report.json')
