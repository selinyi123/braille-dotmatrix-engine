import json

from braille_dotmatrix_engine import create_demo_image
from braille_dotmatrix_engine.cli import main


def test_cli_validation_only_report(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    output_brf = tmp_path / 'out.brf'
    report_json = tmp_path / 'report.json'

    rc = main([
        image,
        '--width-cells', '12',
        '--mode', 'TACTILE',
        '--output-png', str(tmp_path / 'out.png'),
        '--output-txt', str(tmp_path / 'out.txt'),
        '--output-brf', str(output_brf),
        '--brf-validate-only',
        '--report-json', str(report_json),
    ])

    assert rc == 0
    assert not output_brf.exists()
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['artifacts']['brf'] is None
    assert report['artifact_manifest']['brf']['path'] is None
    assert report['brf_export']['validate_only'] is True
    assert report['brf_export']['bytes'] == 0
    assert report['brf_export']['summary'].startswith('BRF ')


def test_cli_brf_preflight_skips_image_render(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('⠁⠃⠉', encoding='utf-8')
    report_json = tmp_path / 'preflight.json'

    rc = main([
        '--brf-preflight', str(source),
        '--brf-profile', 'portable-34x25',
        '--brf-cols', '12',
        '--brf-rows', '5',
        '--report-json', str(report_json),
    ])

    assert rc == 0
    assert report_json.exists()
    assert not (tmp_path / 'output_braille.png').exists()
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['mode'] == 'BRF_PREFLIGHT'
    assert report['renderer']['braille_pipeline_executed'] is False
    assert report['artifact_manifest']['txt']['path'].endswith('source.txt')
    assert report['artifact_manifest']['png']['path'] is None
    assert report['artifact_manifest']['brf']['path'] is None
    assert report['brf_export']['validate_only'] is True
    assert report['brf_export']['summary'].startswith('BRF ok;')


def test_cli_brf_preflight_strict_reports_exit_code(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('A', encoding='utf-8')
    report_json = tmp_path / 'preflight.json'

    rc = main([
        '--brf-preflight', str(source),
        '--strict-brf',
        '--report-json', str(report_json),
    ])

    assert rc == 2
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['mode'] == 'BRF_PREFLIGHT'
    assert report['brf_export']['validate_only'] is True
    assert report['brf_export']['diagnostics']['total'] == 1
    assert report['brf_export']['summary'].startswith('BRF issues;')
