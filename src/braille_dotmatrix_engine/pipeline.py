from __future__ import annotations
import json, time
from dataclasses import asdict
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from .config import BrailleArtConfig
from .dither import correct_over_dense_regions, select_best_dither
from .preprocess import apply_clahe_lab
from .raster import physical_compliance_check, raster_roundtrip_check, render_braille_png
from .sampling import build_dot_grid, process_tiles
from .braille_unicode import braille_matrix_to_text, encode_to_braille_matrix, unicode_roundtrip_test

def create_demo_image(path='test_input.png', size=512):
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for x in range(size):
        arr[:, x] = int(255 * x / max(1, size - 1))
    image = Image.fromarray(arr)
    draw = ImageDraw.Draw(image)
    draw.ellipse((size//3, size//3, 2*size//3, 2*size//3), fill=(255,255,255))
    draw.text((size//12, size//2), 'BRAILLE', fill=(0,0,0))
    image.save(path)
    return str(path)

def process_image(image_path, cfg: BrailleArtConfig, output_png='output_braille.png', output_txt='output_braille.txt', report_json='render_report.json'):
    start = time.time()
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f'Image not found: {image_path}')
    h, w = img.shape[:2]
    enhanced = apply_clahe_lab(img, cfg.clahe_clip_limit, cfg.clahe_grid_size)
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    coords, dx, dy, _ = build_dot_grid(cfg, gray.shape)
    values = process_tiles(gray, coords, cfg)
    if cfg.invert_luminance:
        values = 1.0 - values
    method, binary = select_best_dither(values, cfg.dither_candidates)
    binary = correct_over_dense_regions(binary, cfg)
    text = braille_matrix_to_text(encode_to_braille_matrix(binary))
    Path(output_txt).write_text(text, encoding='utf-8')
    render_braille_png(binary, cfg, output_png)
    report = {'image_shape': [h, w], 'dots_shape': [dy, dx], 'cells_shape': [dy//4, dx//2], 'dither_method': method, 'occupancy_ratio': float(binary.mean()), 'runtime_sec': time.time() - start, 'seed': cfg.seed, 'mode': cfg.mode, 'validation': {'unicode_roundtrip': unicode_roundtrip_test(), 'physical_compliance': physical_compliance_check(binary, cfg), 'raster_roundtrip': raster_roundtrip_check(binary, output_png, cfg)}, 'config': asdict(cfg)}
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report
