from __future__ import annotations
import json, time
from dataclasses import asdict
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from .ascii_backend import write_ascii_output
from .braille_enhance import enhance_sampled_values
from .config import BrailleArtConfig
from .dither import correct_over_dense_regions, select_best_dither
from .metrics import compute_quality_metrics
from .preprocess import apply_clahe_lab
from .raster import physical_compliance_check, raster_roundtrip_check, render_braille_png
from .sampling import build_dot_grid, process_tiles
from .tactile import geometry_report, validate_tactile_output
from .vector import export_svg
from .braille_unicode import braille_matrix_to_text, encode_to_braille_matrix, unicode_roundtrip_test
from .chromatic import render_chromatic_png


def create_demo_image(path='test_input.png', size=512):
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for x in range(size):
        arr[:, x] = int(255 * x / max(1, size - 1))
    image = Image.fromarray(arr)
    draw = ImageDraw.Draw(image)
    draw.ellipse((size//3, size//3, 2*size//3, 2*size//3), fill=(255,255,255))
    draw.text((size//12, size//2), 'BRAILLE', fill=(0,0,0))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return str(path)


def _prepare_outputs(*paths):
    for path in paths:
        if path is not None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)


def process_image(image_path, cfg: BrailleArtConfig, output_png='output_braille.png', output_txt='output_braille.txt', report_json='render_report.json', output_svg=None):
    start = time.time()
    _prepare_outputs(output_png, output_txt, report_json, output_svg)
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
    values = enhance_sampled_values(values, cfg)
    method, binary = select_best_dither(values, cfg.dither_candidates)
    binary = correct_over_dense_regions(binary, cfg)
    tactile_validation = validate_tactile_output(binary, cfg)
    if cfg.mode == 'TACTILE' and bool(getattr(cfg, 'strict_tactile_validation', False)) and not tactile_validation['compliant']:
        raise ValueError('tactile validation failed: ' + json.dumps(tactile_validation['issues'], ensure_ascii=False))
    quality = compute_quality_metrics(values, binary, cfg)
    braille_text = braille_matrix_to_text(encode_to_braille_matrix(binary))
    ascii_report = None
    chromatic_report = None
    if cfg.mode in {'ASCII_MONO', 'ASCII_COLOR'}:
        ascii_report = write_ascii_output(img, cfg, output_txt, color=(cfg.mode == 'ASCII_COLOR'))
        render_braille_png(binary, cfg, output_png)
    else:
        Path(output_txt).write_text(braille_text, encoding='utf-8')
        if cfg.mode == 'CHROMATIC':
            chromatic_report = render_chromatic_png(binary, img, cfg, output_png)
        else:
            render_braille_png(binary, cfg, output_png)
    svg_report = export_svg(binary, cfg, output_svg) if output_svg is not None else None
    raster_check = raster_roundtrip_check(binary, output_png, cfg) if cfg.mode == 'TACTILE' else {'ok': None, 'skipped': 'non-tactile mode uses antialias/glow/color/text'}
    report = {
        'schema_version': '1.8',
        'image_shape': [h, w],
        'dots_shape': [dy, dx],
        'cells_shape': [dy//4, dx//2],
        'dither_method': method,
        'occupancy_ratio': float(binary.mean()),
        'quality_metrics': quality,
        'tactile_geometry': geometry_report(cfg),
        'tactile_export': svg_report,
        'chromatic_render': chromatic_report,
        'ascii_render': ascii_report,
        'braille_enhancement': {
            'preserve_edges': bool(getattr(cfg, 'braille_preserve_edges', True)),
            'edge_weight': float(getattr(cfg, 'braille_edge_weight', 0.0)),
            'gamma': float(getattr(cfg, 'braille_gamma', 1.0)),
            'contrast': float(getattr(cfg, 'braille_contrast', 1.0)),
        },
        'runtime_sec': time.time() - start,
        'seed': cfg.seed,
        'mode': cfg.mode,
        'validation': {
            'unicode_roundtrip': unicode_roundtrip_test(),
            'physical_compliance': physical_compliance_check(binary, cfg),
            'tactile_output': tactile_validation,
            'raster_roundtrip': raster_check,
        },
        'config': asdict(cfg),
    }
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report
