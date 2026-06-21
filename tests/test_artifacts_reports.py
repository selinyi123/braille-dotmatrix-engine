from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image


def test_process_image_report_versions(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_html=True),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        tmp_path / 'report.json',
    )
    assert report['package_version'].startswith('1.18')
    assert report['schema_version'] == '1.11'
    assert report['renderer']['strategy'] == 'AsciiMonoRenderer'
