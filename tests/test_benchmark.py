import csv
import json

import braille_dotmatrix_engine.benchmark as benchmark_mod
from braille_dotmatrix_engine.benchmark import (
    BENCHMARK_SCHEMA_VERSION,
    create_synthetic_image,
    main,
    run_one_benchmark,
    validate_benchmark_rows,
    write_benchmark_csv,
    write_benchmark_summary,
)
from braille_dotmatrix_engine.schema import RENDER_SCHEMA_VERSION


def test_create_synthetic_image(tmp_path):
    path = create_synthetic_image(tmp_path / 'synthetic.png', width=64, height=48)
    assert (tmp_path / 'synthetic.png').exists()
    assert path.endswith('synthetic.png')


def test_run_one_benchmark_returns_metrics(tmp_path):
    row = run_one_benchmark('unit', (48, 64), 'TACTILE', output_dir=tmp_path)
    assert row['schema_version'] == RENDER_SCHEMA_VERSION
    assert row['benchmark_schema_version'] == BENCHMARK_SCHEMA_VERSION
    assert row['runtime_sec'] >= 0
    assert row['width'] == 64
    assert row['height'] == 48
    assert 0 <= row['occupancy_ratio'] <= 1


def test_validate_benchmark_rows_detects_bad_values():
    rows = [{
        'name': 'bad',
        'mode': 'TACTILE',
        'runtime_sec': 999,
        'rss_peak_mb': 1,
        'occupancy_ratio': 0.5,
        'schema_version': RENDER_SCHEMA_VERSION,
        'benchmark_schema_version': BENCHMARK_SCHEMA_VERSION,
    }]
    issues = validate_benchmark_rows(rows, max_runtime_sec=1, max_rss_peak_mb=10)
    assert issues


def test_write_benchmark_csv_and_summary(tmp_path):
    rows = [{
        'name': 'unit',
        'mode': 'TACTILE',
        'runtime_sec': 0.1,
        'rss_peak_mb': 1.0,
        'occupancy_ratio': 0.5,
        'schema_version': RENDER_SCHEMA_VERSION,
        'benchmark_schema_version': BENCHMARK_SCHEMA_VERSION,
    }]
    csv_path = write_benchmark_csv(rows, tmp_path / 'benchmark.csv')
    summary_path = write_benchmark_summary(rows, tmp_path / 'summary.json')
    with open(csv_path, newline='', encoding='utf-8') as f:
        loaded = list(csv.DictReader(f))
    assert loaded[0]['name'] == 'unit'
    summary = json.loads(open(summary_path, encoding='utf-8').read())
    assert summary['ok'] is True
    assert summary['render_schema_version'] == RENDER_SCHEMA_VERSION


def test_rss_fallback_without_resource(monkeypatch):
    monkeypatch.setattr(benchmark_mod, 'resource', None)
    assert benchmark_mod._rss_mb() == 0.0


def test_benchmark_module_main_writes_artifacts(tmp_path):
    code = main([
        '--output-dir', str(tmp_path / 'bench'),
        '--csv', str(tmp_path / 'bench' / 'benchmark.csv'),
        '--summary', str(tmp_path / 'bench' / 'summary.json'),
        '--no-ascii',
        '--max-runtime-sec', '120',
        '--max-rss-mb', '4096',
    ])
    assert code == 0
    assert (tmp_path / 'bench' / 'benchmark.csv').exists()
    assert (tmp_path / 'bench' / 'summary.json').exists()
