from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image, render_ascii_text


def test_ascii_text_shape_and_charset():
    import numpy as np
    source = np.zeros((24, 48, 3), dtype=np.uint8)
    source[:, :, 0] = 255
    cfg = BrailleArtConfig(mode='ASCII_MONO', output_width_cells=24, ascii_charset=' .#')
    text, report = render_ascii_text(source, cfg)
    lines = text.rstrip('\n').split('\n')
    assert report['backend'] == 'ASCII_MONO'
    assert report['cols'] == 24
    assert len(lines) == report['rows']


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
    assert report['package_version'].startswith('1.18')
    assert report['renderer']['strategy'] == 'AsciiMonoRenderer'
    assert report['ascii_render']['backend'] == 'ASCII_MONO'
    assert report['diagnostics']['braille_pipeline']['executed'] is False
    assert report['artifact_manifest']['png']['exists'] is True
