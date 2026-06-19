import csv

from braille_dotmatrix_engine.benchmark import create_synthetic_image, run_one_benchmark, write_benchmark_csv


def test_create_synthetic_image(tmp_path):
    path = create_synthetic_image(tmp_path / 'synthetic.png', width=64, height=48)
    assert (tmp_path / 'synthetic.png').exists()
    assert path.endswith('synthetic.png')


def test_run_one_benchmark_returns_metrics(tmp_path):
    row = run_one_benchmark('unit', (48, 64), 'TACTILE', output_dir=tmp_path)
    assert row['schema_version'] == '1.9'
    assert row['runtime_sec'] >= 0
    assert row['width'] == 64
    assert row['height'] == 48
    assert 0 <= row['occupancy_ratio'] <= 1


def test_write_benchmark_csv(tmp_path):
    rows = [{'name': 'unit', 'mode': 'TACTILE', 'runtime_sec': 0.1}]
    csv_path = write_benchmark_csv(rows, tmp_path / 'benchmark.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        loaded = list(csv.DictReader(f))
    assert loaded[0]['name'] == 'unit'
