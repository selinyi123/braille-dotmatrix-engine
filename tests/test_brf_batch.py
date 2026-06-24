import json
from pathlib import Path

import pytest

from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files
from braille_dotmatrix_engine.cli import main
from braille_dotmatrix_engine.schema import BRF_SCHEMA_VERSION

EXAMPLES = Path('examples/brf')


def test_resolve_brf_input_paths_for_directory():
    paths = resolve_brf_input_paths(EXAMPLES, '*.txt')
    names = [path.name for path in paths]
    assert names == ['eight_dot_error.txt', 'non_braille_warning.txt', 'valid_six_dot.txt']


def test_resolve_brf_input_paths_supports_recursive_scan(tmp_path):
    root = tmp_path / 'root'
    nested = root / 'nested'
    nested.mkdir(parents=True)
    (nested / 'sample.txt').write_text('⠁', encoding='utf-8')
    with pytest.raises(FileNotFoundError):
        resolve_brf_input_paths(root, '*.txt')
    paths = resolve_brf_input_paths(root, '*.txt', recursive=True)
    assert [path.name for path in paths] == ['sample.txt']


def test_resolve_brf_input_paths_rejects_too_many_files():
    with pytest.raises(ValueError, match='too many BRF input files'):
        resolve_brf_input_paths(EXAMPLES, '*.txt', max_files=2)


def test_validate_brf_files_aggregate_examples():
    paths = resolve_brf_input_paths(EXAMPLES, '*.txt')
    report = validate_brf_files(paths)
    aggregate = report['aggregate']
    assert report['brf_schema_version'] == BRF_SCHEMA_VERSION
    assert aggregate['brf_schema_version'] == BRF_SCHEMA_VERSION
    assert aggregate['total_files'] == 3
    assert aggregate['ok_files'] == 1
    assert aggregate['warning_files'] == 1
    assert aggregate['error_files'] == 1
    assert aggregate['issue_files'] == 2
    assert aggregate['warning_count'] == 1
    assert aggregate['error_count'] == 1
    assert aggregate['truncated_files'] == 0
    assert aggregate['total_bytes'] > 0
    assert aggregate['by_reason']['non_braille_character'] == 1
    assert aggregate['by_reason']['dots_7_or_8_not_supported'] == 1


def test_validate_brf_files_rejects_oversized_file(tmp_path):
    source = tmp_path / 'large.txt'
    source.write_text('A' * 20, encoding='utf-8')
    with pytest.raises(ValueError, match='too large'):
        validate_brf_files([source], max_file_bytes=10)


def test_validate_brf_files_caps_diagnostics(tmp_path):
    source = tmp_path / 'warnings.txt'
    source.write_text('ABC', encoding='utf-8')
    report = validate_brf_files([source], diagnostics_limit=1)
    file_report = report['files'][0]
    assert file_report['diagnostics_truncated'] is True
    assert file_report['brf_export']['unsupported_count'] == 3
    assert len(file_report['brf_export']['unsupported']) == 1
    assert report['aggregate']['truncated_files'] == 1


def test_cli_brf_preflight_batch_report(tmp_path):
    report_json = tmp_path / 'batch.json'
    rc = main([
        '--brf-preflight-batch', str(EXAMPLES),
        '--report-json', str(report_json),
    ])
    assert rc == 0
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['mode'] == 'BRF_PREFLIGHT_BATCH'
    assert report['brf_schema_version'] == BRF_SCHEMA_VERSION
    assert report['batch']['recursive'] is False
    assert report['batch']['aggregate']['total_files'] == 3
    assert report['batch']['aggregate']['ok_files'] == 1
    assert len(report['batch']['files']) == 3


def test_cli_brf_preflight_batch_recursive_report(tmp_path):
    root = tmp_path / 'root'
    nested = root / 'nested'
    nested.mkdir(parents=True)
    (nested / 'sample.txt').write_text('⠁', encoding='utf-8')
    report_json = tmp_path / 'batch.json'
    rc = main([
        '--brf-preflight-batch', str(root),
        '--brf-batch-recursive',
        '--report-json', str(report_json),
    ])
    assert rc == 0
    report = json.loads(report_json.read_text(encoding='utf-8'))
    assert report['batch']['recursive'] is True
    assert report['batch']['aggregate']['total_files'] == 1


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
