import numpy as np
import pytest

from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image, render_ascii_text


def test_ascii_text_shape_and_charset():
    source = np.zeros((24, 48, 3), dtype=np.uint8)
    source[:, :, 0] = 255
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=24, ascii_charset=' .#')
    text, report = render_ascii_text(source, cfg)
    lines = text.rstrip('\n').split('\n')
    assert report['backend'] == 'ASCII_MONO'
    assert report['cols'] == 24
    assert len(lines) == report['rows']


def test_ascii_backend_rejects_empty_image():
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=8)
    with pytest.raises(ValueError, match='non-empty'):
        render_ascii_text(np.zeros((0, 8, 3), dtype=np.uint8), cfg)


def test_ascii_backend_rejects_one_dimensional_input():
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=8)
    with pytest.raises(ValueError, match='2D grayscale or 3D color'):
        render_ascii_text(np.zeros((8,), dtype=np.uint8), cfg)


def test_ascii_backend_rejects_fractional_width_for_direct_api_calls():
    source = np.zeros((16, 16, 3), dtype=np.uint8)
    cfg = BrailleArtConfig(mode='ASCII_MONO')
    cfg.output_width_cells = 8.5
    with pytest.raises(ValueError, match='output_width_cells'):
        render_ascii_text(source, cfg)


def test_ascii_backend_rejects_oversized_direct_grid():
    source = np.zeros((32, 32, 3), dtype=np.uint8)
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=16, max_total_dots=64)
    with pytest.raises(ValueError, match='max_total_dots'):
        render_ascii_text(source, cfg)


def test_process_image_ascii_report(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_charset_preset='standard'),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        tmp_path / 'report.json',
    )
    assert report['schema_version'] == '1.11'
    assert report['package_version']
    assert report['renderer']['strategy'] == 'AsciiMonoRenderer'
    assert report['ascii_render']['backend'] == 'ASCII_MONO'
    assert report['diagnostics']['braille_pipeline']['executed'] is False
    assert report['artifact_manifest']['png']['exists'] is True
