import json

import numpy as np
from PIL import Image

from braille_dotmatrix_engine import (
    BrailleArtConfig,
    create_demo_image,
    process_image,
    render_ascii_html,
    render_ascii_png,
    render_ascii_text,
    resolve_ascii_charset,
)


def test_ascii_text_shape_and_charset():
    source = np.zeros((24, 48, 3), dtype=np.uint8)
    source[:, :, 0] = 255
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=24, ascii_charset=' .#')
    text, report = render_ascii_text(source, cfg)
    lines = text.rstrip('\n').split('\n')
    assert report['backend'] == 'ASCII_MONO'
    assert report['cols'] == 24
    assert len(lines) == report['rows']
    assert all(len(line) == 24 for line in lines)
    assert 'quality' in report


def test_ascii_color_contains_ansi_codes():
    source = np.zeros((12, 24, 3), dtype=np.uint8)
    source[:, :, 2] = 220
    cfg = BrailleArtConfig(mode='ASCII_COLOR', output_width_cells=12)
    text, report = render_ascii_text(source, cfg, color=True)
    assert report['backend'] == 'ASCII_COLOR'
    assert '\x1b[38;2;' in text


def test_ascii_preset_and_html_render():
    source = np.zeros((12, 24, 3), dtype=np.uint8)
    source[:, :, 1] = 200
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=12, ascii_charset_preset='blocks')
    charset, preset = resolve_ascii_charset(cfg)
    html, quality = render_ascii_html(source, cfg)
    assert preset == 'blocks'
    assert '█' in charset
    assert '<!doctype html>' in html
    assert 'tone_score' in quality


def test_ascii_png_preview(tmp_path):
    source = np.zeros((12, 24, 3), dtype=np.uint8)
    source[:, :, 2] = 220
    cfg = BrailleArtConfig(mode='ASCII_COLOR', output_width_cells=12)
    report = render_ascii_png(source, cfg, tmp_path / 'ascii.png', color=True)
    assert (tmp_path / 'ascii.png').exists()
    loaded = Image.open(tmp_path / 'ascii.png')
    assert loaded.mode == 'RGB'
    assert loaded.size[0] == report['width_px']
    assert loaded.size[1] == report['height_px']


def test_process_image_ascii_report(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report_path = tmp_path / 'report.json'
    html_path = tmp_path / 'ascii.html'
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_charset_preset='standard'),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        report_path,
        None,
        html_path,
    )
    assert report['schema_version'] == '1.9'
    assert report['ascii_render']['backend'] == 'ASCII_MONO'
    assert report['ascii_render']['charset_preset'] == 'standard'
    assert report['ascii_render']['png_preview']['png_path'].endswith('out.png')
    assert (tmp_path / 'ascii.txt').exists()
    assert html_path.exists()
    assert Image.open(tmp_path / 'out.png').mode == 'RGB'
    assert json.loads(report_path.read_text(encoding='utf-8'))['mode'] == 'ASCII_MONO'


def test_process_image_ascii_html_default_path(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_html=True),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        tmp_path / 'report.json',
    )
    assert (tmp_path / 'ascii.html').exists()
    assert report['ascii_render']['html_path'].endswith('ascii.html')
