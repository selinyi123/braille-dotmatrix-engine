import json

import numpy as np

from braille_dotmatrix_engine import (
    BrailleArtConfig,
    create_demo_image,
    process_image,
    render_ascii_html,
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
    assert (tmp_path / 'ascii.txt').exists()
    assert html_path.exists()
    assert json.loads(report_path.read_text(encoding='utf-8'))['mode'] == 'ASCII_MONO'
