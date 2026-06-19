from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image


def test_process_image_creates_nested_output_dirs(tmp_path):
    image = create_demo_image(tmp_path / 'input' / 'demo.png', size=96)
    out_dir = tmp_path / 'deep' / 'outputs'
    report = process_image(image, BrailleArtConfig(output_width_cells=12), out_dir / 'out.png', out_dir / 'out.txt', out_dir / 'report.json')
    assert report['schema_version'] == '1.9'
    assert (out_dir / 'out.png').exists()
    assert (out_dir / 'out.txt').exists()
    assert (out_dir / 'report.json').exists()
