import numpy as np

from braille_dotmatrix_engine import BrailleArtConfig, analyze_braille_quality, apply_density_control


def test_density_control_reports_target_and_adjustment():
    values = np.linspace(0, 1, 100, dtype=np.float32).reshape(10, 10)
    cfg = BrailleArtConfig(braille_target_density=0.30, braille_density_strength=0.8)
    adjusted, report = apply_density_control(values, cfg)
    assert adjusted.shape == values.shape
    assert report['enabled'] is True
    assert report['target_density'] == 0.30
    assert 'estimated_density_after' in report
    assert float(adjusted.min()) >= 0.0
    assert float(adjusted.max()) <= 1.0


def test_braille_quality_seam_report_shape():
    binary = np.zeros((32, 32), dtype=bool)
    binary[:16, :16] = True
    cfg = BrailleArtConfig(braille_seam_tile=8, braille_seam_threshold=0.01)
    report = analyze_braille_quality(binary, cfg)
    assert report['tile_rows'] == 4
    assert report['tile_cols'] == 4
    assert report['dot_density'] > 0
    assert report['seam_score'] >= 0
    assert report['seam_warning'] is True
