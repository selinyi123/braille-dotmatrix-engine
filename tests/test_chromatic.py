import json

import cv2
import numpy as np

from braille_dotmatrix_engine import BrailleArtConfig, build_chromatic_array, create_demo_image, process_image


def test_chromatic_array_shape_and_dtype():
    binary = np.zeros((8, 8), dtype=bool)
    binary[0::2, 0::2] = True
    source = np.zeros((32, 32, 3), dtype=np.uint8)
    source[:, :, 1] = 255
    cfg = BrailleArtConfig(mode='CHROMATIC', chromatic_cell_w_px=8, chromatic_cell_h_px=12, chromatic_luma_threshold=10, chromatic_white_balance=False)
    arr = build_chromatic_array(binary, source, cfg)
    assert arr.dtype == np.uint8
    assert arr.shape == (24, 32, 3)
    assert int(arr.max()) > 0


def test_process_image_chromatic_report(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report_path = tmp_path / 'report.json'
    report = process_image(image, BrailleArtConfig(output_width_cells=12, mode='CHROMATIC'), tmp_path / 'out.png', tmp_path / 'out.txt', report_path)
    assert report['schema_version'] == '1.10'
    assert report['package_version'] == '1.13.0'
    assert report['mode'] == 'CHROMATIC'
    assert report['renderer']['backend'] == 'CHROMATIC'
    assert report['renderer']['strategy'] == 'ChromaticRenderer'
    assert report['renderer']['braille_pipeline_executed'] is True
    assert report['diagnostics']['braille_pipeline']['executed'] is True
    assert report['chromatic_render']['backend'] == 'CHROMATIC'
    assert report['validation']['raster_roundtrip']['ok'] is None
    assert report['artifact_manifest']['png']['exists'] is True
    assert (tmp_path / 'out.png').exists()
    loaded = cv2.imread(str(tmp_path / 'out.png'))
    assert loaded is not None
    assert json.loads(report_path.read_text(encoding='utf-8'))['mode'] == 'CHROMATIC'
