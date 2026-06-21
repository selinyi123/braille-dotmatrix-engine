from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image


def test_process_image_writes_svg_export(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    out_svg = tmp_path / 'out.svg'
    report = process_image(image, BrailleArtConfig(output_width_cells=12), tmp_path / 'out.png', tmp_path / 'out.txt', tmp_path / 'report.json', out_svg)
    assert report['schema_version'] == '1.10'
    assert report['artifact_manifest']['svg']['exists'] is True
    assert report['tactile_export']['dot_count'] >= 0
    assert out_svg.exists()
