import json
from pathlib import Path

from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files
from braille_dotmatrix_engine.cli import main

EXAMPLES = Path('examples/brf')


def test_resolve_brf_input_paths_for_directory():
    paths = resolve_brf_input_paths(EXAMPLES, '*.txt')
    names = [path.name for path in paths]
    assert names == ['eight_dot_error.txt', 'non_braille_warning.txt', 'valid_six_dot.txt']


def test_validate_brf_files_aggregate_examples():
    paths = resolve_brf_input_paths(EXAMPLES, '*.txt')
    report = validate_brf_files(paths)
    aggregate = report['aggregate']
    assert aggregate['total_files'] == 3
    assert aggregate['ok_files'] == 1
    assert aggregate['warning_files'] == 1
    assert aggregate['error_files'] == 1
    assert aggregate['issue_files'] == 2
    assert aggregate['warning_count'] == 1
    assert aggregate['error_count'] == 1
    assert aggregate['by_reason']['non_braille_character'] == 1
    assert aggregate['by_reason']['dots_7_or_8_not_supported'] == 1


def test_cli_brf_preflight_batch_report(tmp_path):
    report_json = tmp_path / 'batch.json'
    rc = main([
        '--brf-preflight-batch', str(EXAMPLES),
        '--report-json', str(report_json),
    ])
    assert rc == 0
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['mode'] == 'BRF_PREFLIGHT_BATCH'
    assert report['batch']['aggregate']['total_files'] == 3
    assert report['batch']['aggregate']['ok_files'] == 1
    assert len(report['batch']['files']) == 3


def test_cli_brf_preflight_batch_strict_exit_code(tmp_path):
    report_json = tmp_path / 'batch.json'
    rc = main([
        '--brf-preflight-batch', str(EXAMPLES),
        '--strict-brf',
        '--report-json', str(report_json),
    ])
    assert rc == 2
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['batch']['aggregate']['issue_files'] == 2
