from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image
from braille_dotmatrix_engine.renderers import get_renderer, renderer_names


def test_renderer_registry_contains_all_public_modes():
    assert set(renderer_names()) == {'TACTILE', 'SCREEN', 'CHROMATIC', 'ASCII_MONO', 'ASCII_COLOR'}
    assert type(get_renderer('TACTILE')).__name__ == 'TactileRenderer'
    assert type(get_renderer('SCREEN')).__name__ == 'ScreenRenderer'
    assert type(get_renderer('CHROMATIC')).__name__ == 'ChromaticRenderer'
    assert type(get_renderer('ASCII_MONO')).__name__ == 'AsciiMonoRenderer'
    assert type(get_renderer('ASCII_COLOR')).__name__ == 'AsciiColorRenderer'


def test_tactile_process_image_reports_renderer_strategy(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='TACTILE'),
        tmp_path / 'out.png',
        tmp_path / 'out.txt',
        tmp_path / 'report.json',
    )
    assert report['package_version'] == '1.13.0'
    assert report['schema_version'] == '1.10'
    assert report['renderer']['strategy'] == 'TactileRenderer'
    assert report['renderer']['braille_pipeline_executed'] is True
    assert report['ascii_render'] is None
    assert report['dots_shape'] is not None
    assert report['artifact_manifest']['png']['exists'] is True
