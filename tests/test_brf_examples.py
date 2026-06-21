import json
from pathlib import Path

from braille_dotmatrix_engine.brf import validate_brf_text
from braille_dotmatrix_engine.cli import main

EXAMPLES = Path('examples/brf')


def test_example_valid_six_dot_summary():
    report = validate_brf_text((EXAMPLES / 'valid_six_dot.txt').read_text(encoding='utf-8'))
    assert report['summary'].startswith('BRF ok;')
    assert report['diagnostics']['total'] == 0


def test_example_eight_dot_error_summary():
    report = validate_brf_text((EXAMPLES / 'eight_dot_error.txt').read_text(encoding='utf-8'))
    assert report['summary'].startswith('BRF issues;')
    assert report['error_count'] == 1
    assert report['diagnostics']['by_reason']['dots_7_or_8_not_supported'] == 1


def test_example_non_braille_warning_summary():
    report = validate_brf_text((EXAMPLES / 'non_braille_warning.txt').read_text(encoding='utf-8'))
    assert report['summary'].startswith('BRF issues;')
    assert report['warning_count'] == 1
    assert report['diagnostics']['by_reason']['non_braille_character'] == 1


def test_cli_preflight_example_fixture(tmp_path):
    report_json = tmp_path / 'report.json'
    rc = main([
        '--brf-preflight', str(EXAMPLES / 'valid_six_dot.txt'),
        '--report-json', str(report_json),
    ])
    assert rc == 0
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['mode'] == 'BRF_PREFLIGHT'
    assert report['brf_export']['summary'].startswith('BRF ok;')
