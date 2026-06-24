import json
from pathlib import Path

import pytest

from braille_dotmatrix_engine.cli import main


def test_cli_generates_outputs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(['--width-cells', '12', '--output-png', 'cli.png', '--output-txt', 'cli.txt', '--report-json', 'cli.json']) == 0
    assert (tmp_path / 'cli.png').exists()
    assert (tmp_path / 'cli.txt').exists()
    assert (tmp_path / 'cli.json').exists()


def test_cli_chromatic_mode_generates_outputs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(['--width-cells', '12', '--mode', 'CHROMATIC', '--output-png', 'chromatic.png', '--output-txt', 'chromatic.txt', '--report-json', 'chromatic.json']) == 0
    assert (tmp_path / 'chromatic.png').exists()
    assert (tmp_path / 'chromatic.txt').exists()
    assert (tmp_path / 'chromatic.json').exists()


def test_cli_ascii_mode_generates_outputs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(['--width-cells', '12', '--mode', 'ASCII_MONO', '--output-png', 'ascii.png', '--output-txt', 'ascii.txt', '--report-json', 'ascii.json']) == 0
    assert (tmp_path / 'ascii.png').exists()
    assert (tmp_path / 'ascii.txt').exists()
    assert (tmp_path / 'ascii.json').exists()


def test_cli_ascii_html_and_quality_controls(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main([
        '--width-cells', '12',
        '--mode', 'ASCII_COLOR',
        '--ascii-preset', 'blocks',
        '--ascii-html',
        '--output-html', 'ascii.html',
        '--braille-target-density', '0.35',
        '--output-png', 'ascii.png',
        '--output-txt', 'ascii.ansi',
        '--report-json', 'ascii.json',
    ]) == 0
    assert (tmp_path / 'ascii.html').exists()
    assert (tmp_path / 'ascii.ansi').exists()
    assert (tmp_path / 'ascii.json').exists()


def test_cli_rejects_non_finite_ascii_float_arguments(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(['--mode', 'ASCII_MONO', '--ascii-aspect', 'nan'])
    assert exc.value.code == 2
    with pytest.raises(SystemExit) as exc:
        main(['--mode', 'ASCII_MONO', '--ascii-edge-weight', 'inf'])
    assert exc.value.code == 2


def test_cli_rejects_brf_export_for_ascii_mode(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(['--mode', 'ASCII_MONO', '--output-brf', 'ascii.brf'])
    assert exc.value.code == 2
    assert not (tmp_path / 'ascii.brf').exists()


def test_cli_rejects_mutually_exclusive_task_modes(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(['--benchmark', '--brf-preflight', 'input.txt'])
    assert exc.value.code == 2


def test_cli_writes_brf_for_braille_backed_mode(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code = main([
        '--width-cells', '8',
        '--mode', 'TACTILE',
        '--output-png', 'out.png',
        '--output-txt', 'out.txt',
        '--report-json', 'report.json',
        '--output-brf', 'out.brf',
    ])
    assert code == 0
    assert (tmp_path / 'out.brf').exists()
    persisted = json.loads((tmp_path / 'report.json').read_text(encoding='utf-8'))
    assert persisted['artifact_manifest']['brf']['exists'] is True
    assert persisted['brf_export']['path'].endswith('out.brf')


def test_cli_benchmark_ignores_render_only_brf_options(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code = main(['--benchmark', '--mode', 'ASCII_MONO', '--output-brf', 'ignored.brf', '--benchmark-csv', 'bench.csv'])
    assert code == 0
    assert (tmp_path / 'bench.csv').exists()
    assert not (tmp_path / 'ignored.brf').exists()


def test_cli_benchmark_generates_csv(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(['--benchmark', '--benchmark-csv', 'bench.csv']) == 0
    assert (tmp_path / 'bench.csv').exists()
