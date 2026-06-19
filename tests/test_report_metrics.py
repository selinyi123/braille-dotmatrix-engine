from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image


def test_report_contains_quality_metrics(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    cfg = BrailleArtConfig(output_width_cells=12, tile_size_px=48, tile_overlap_px=12, render_spacing_px=6)
    report = process_image(image, cfg, tmp_path / 'out.png', tmp_path / 'out.txt', tmp_path / 'report.json')
    assert report['schema_version'] == '1.9'
    assert 'quality_metrics' in report
    assert 'mse' in report['quality_metrics']
    assert 'occupancy' in report['quality_metrics']
    assert 'tactile_geometry' in report
    assert 'braille_enhancement' in report
    assert 'braille_quality' in report
    assert 'braille_density_control' in report
