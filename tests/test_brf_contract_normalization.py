import json
from pathlib import Path

from braille_dotmatrix_engine.brf_batch import resolve_brf_input_paths, validate_brf_files
from braille_dotmatrix_engine.brf_contract import batch_contract_from_report, main, write_batch_contract_from_report

EXAMPLES = Path('examples/brf')
SNAPSHOT = EXAMPLES / 'snapshots' / 'batch_examples.json'


def test_batch_contract_from_report_matches_checked_in_snapshot():
    batch = validate_brf_files(resolve_brf_input_paths(EXAMPLES, '*.txt'))
    report = {'mode': 'BRF_PREFLIGHT_BATCH', 'batch': batch}
    expected = json.loads(SNAPSHOT.read_text(encoding='utf-8'))

    assert batch_contract_from_report(report) == expected


def test_batch_contract_from_contract_is_idempotent():
    expected = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    assert batch_contract_from_report(expected) == expected


def test_write_batch_contract_from_report(tmp_path):
    batch = validate_brf_files(resolve_brf_input_paths(EXAMPLES, '*.txt'))
    report = tmp_path / 'report.json'
    output = tmp_path / 'contract.json'
    report.write_text(json.dumps({'batch': batch}), encoding='utf-8')

    contract = write_batch_contract_from_report(report, output)

    assert contract == json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    assert json.loads(output.read_text(encoding='utf-8')) == contract


def test_cli_writes_batch_contract(tmp_path):
    batch = validate_brf_files(resolve_brf_input_paths(EXAMPLES, '*.txt'))
    report = tmp_path / 'report.json'
    output = tmp_path / 'contract.json'
    report.write_text(json.dumps({'batch': batch}), encoding='utf-8')

    rc = main([str(report), '--output', str(output)])

    assert rc == 0
    assert json.loads(output.read_text(encoding='utf-8')) == json.loads(SNAPSHOT.read_text(encoding='utf-8'))
