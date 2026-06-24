import json

from braille_dotmatrix_engine import create_demo_image
from braille_dotmatrix_engine.cli import main


def test_cli_writes_brf_and_updates_report(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    output_png = tmp_path / 'out.png'
    output_txt = tmp_path / 'out.txt'
    output_brf = tmp_path / 'out.brf'
    report_json = tmp_path / 'report.json'

    rc = main([
        image,
        '--width-cells', '12',
        '--mode', 'TACTILE',
        '--output-png', str(output_png),
        '--output-txt', str(output_txt),
        '--output-brf', str(output_brf),
        '--brf-profile', 'portable-34x25',
        '--brf-cols', '12',
        '--brf-rows', '5',
        '--report-json', str(report_json),
    ])

    assert rc == 0
    assert output_brf.exists()
    assert output_brf.read_text(encoding='ascii')
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['package_version']
    assert report['schema_version'] == '1.12'
    assert report['artifacts']['brf'].endswith('out.brf')
    assert report['artifact_manifest']['brf']['exists'] is True
    assert report['brf_export']['path'].endswith('out.brf')
    assert report['brf_export']['profile'] == 'portable-34x25+override'
    assert report['brf_export']['cols'] == 12
    assert report['brf_export']['rows'] == 5
    assert report['brf_export']['diagnostics']['total'] >= 0
    assert report['brf_export']['summary'].startswith('BRF ')
