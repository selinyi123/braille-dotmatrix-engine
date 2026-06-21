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
