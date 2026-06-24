import json

import cv2
import numpy as np

from braille_dotmatrix_engine import BrailleArtConfig, process_image
from braille_dotmatrix_engine.json_utils import dumps_json


def test_dumps_json_replaces_non_finite_floats_with_null():
    text = dumps_json({'nan': float('nan'), 'inf': float('inf'), 'nested': [float('-inf')]})
    assert 'NaN' not in text
    assert 'Infinity' not in text
    assert json.loads(text) == {'nan': None, 'inf': None, 'nested': [None]}


def test_dumps_json_serializes_sets_deterministically():
    payload = {'items': set(['b', 'a', 'c'])}
    text = dumps_json(payload)
    assert json.loads(text) == {'items': ['a', 'b', 'c']}


def test_render_report_is_strict_json_for_constant_image(tmp_path):
    image = tmp_path / 'constant.png'
    cv2.imwrite(str(image), np.zeros((64, 64, 3), dtype=np.uint8))
    report_json = tmp_path / 'report.json'

    process_image(
        image,
        BrailleArtConfig(output_width_cells=8, mode='TACTILE'),
        tmp_path / 'out.png',
        tmp_path / 'out.txt',
        report_json,
    )

    text = report_json.read_text(encoding='utf-8')
    assert 'NaN' not in text
    assert 'Infinity' not in text
    parsed = json.loads(text)
    json.dumps(parsed, allow_nan=False)
    assert parsed['artifact_manifest']['report_json']['exists'] is True


def test_pipeline_accepts_grayscale_image_via_preprocess(tmp_path):
    image = tmp_path / 'gray.png'
    cv2.imwrite(str(image), np.zeros((32, 32), dtype=np.uint8))
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=4, mode='TACTILE'),
        tmp_path / 'out.png',
        tmp_path / 'out.txt',
        tmp_path / 'report.json',
    )
    assert report['image_shape'] == [32, 32]
