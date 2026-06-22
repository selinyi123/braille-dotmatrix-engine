import json
from pathlib import Path

from braille_dotmatrix_engine.brf import validate_brf_text
from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files

EXAMPLES = Path('examples/brf')
CONTRACTS = EXAMPLES / 'snapshots'


def _load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _single_contract(report: dict) -> dict:
    return {
        'summary': report['summary'],
        'ok': report['ok'],
        'validate_only': report['validate_only'],
        'unsupported_count': report['unsupported_count'],
        'warning_count': report['warning_count'],
        'error_count': report['error_count'],
        'diagnostics': report['diagnostics'],
        'unsupported': report['unsupported'],
    }


def _batch_contract(report: dict) -> dict:
    return {
        'aggregate': report['aggregate'],
        'files': [
            {
                'name': Path(item['path']).name,
                'summary': item['summary'],
                'ok': item['ok'],
                'warning_count': item['warning_count'],
                'error_count': item['error_count'],
            }
            for item in report['files']
        ],
    }


def test_valid_six_dot_contract():
    report = validate_brf_text((EXAMPLES / 'valid_six_dot.txt').read_text(encoding='utf-8'))
    assert _single_contract(report) == _load_contract(CONTRACTS / 'valid_six_dot.json')


def test_eight_dot_error_contract():
    report = validate_brf_text((EXAMPLES / 'eight_dot_error.txt').read_text(encoding='utf-8'))
    assert _single_contract(report) == _load_contract(CONTRACTS / 'eight_dot_error.json')


def test_non_braille_warning_contract():
    report = validate_brf_text((EXAMPLES / 'non_braille_warning.txt').read_text(encoding='utf-8'))
    assert _single_contract(report) == _load_contract(CONTRACTS / 'non_braille_warning.json')


def test_batch_examples_contract():
    paths = resolve_brf_input_paths(EXAMPLES, '*.txt')
    report = validate_brf_files(paths)
    assert _batch_contract(report) == _load_contract(CONTRACTS / 'batch_examples.json')
