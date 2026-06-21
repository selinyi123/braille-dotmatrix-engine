from __future__ import annotations
import json, time
from dataclasses import asdict
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from .ascii_backend import write_ascii_output
from .braille_enhance import enhance_sampled_values
from .braille_quality import analyze_braille_quality, apply_density_control
from .config import BrailleArtConfig
from .dither import correct_over_dense_regions, select_best_dither
from .metrics import compute_quality_metrics
from .preprocess import apply_clahe_lab
from .raster import physical_compliance_check, raster_roundtrip_check, render_braille_png
from .sampling import build_dot_grid, process_tiles
from .schema import PACKAGE_VERSION, RENDER_SCHEMA_VERSION
from .tactile import geometry_report, validate_tactile_output
from .validation import validate_config
from .vector import export_svg
from .braille_unicode import braille_matrix_to_text, encode_to_braille_matrix, unicode_roundtrip_test
from .chromatic import render_chromatic_png


ASCII_MODES = {'ASCII_MONO', 'ASCII_COLOR'}


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


def _resolve_html_output(cfg: BrailleArtConfig, output_txt, output_html):
    if output_html is not None:
        return output_html
    if cfg.mode in ASCII_MODES and bool(getattr(cfg, 'ascii_html', False)):
        return Path(output_txt).with_suffix('.html')
    return None


def _load_image(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f'Image not found: {image_path}')
    return img


def _artifact_report(output_png, output_txt, report_json, output_svg, output_html) -> dict:
    return {
        'png': None if output_png is None else str(output_png),
        'txt': None if output_txt is None else str(output_txt),
        'report_json': None if report_json is None else str(report_json),
        'svg': None if output_svg is None else str(output_svg),
        'html': None if output_html is None else str(output_html),
    }


def _base_report(img, cfg, start, output_png, output_txt, report_json, output_svg, output_html) -> dict:
    h, w = img.shape[:2]
    return {
        'package_version': PACKAGE_VERSION,
        'schema_version': RENDER_SCHEMA_VERSION,
        'image_shape': [h, w],
        'runtime_sec': time.time() - start,
        'seed': cfg.seed,
        'mode': cfg.mode,
        'renderer': {
            'mode': cfg.mode,
            'backend': cfg.mode,
            'braille_diagnostics_requested': bool(getattr(cfg, 'include_braille_diagnostics', False)),
        },
        'artifacts': _artifact_report(output_png, output_txt, report_json, output_svg, output_html),
        'diagnostics': {},
        'config': asdict(cfg),
    }


def _process_braille_pipeline(img, cfg: BrailleArtConfig, output_png, output_txt, output_svg):
    enhanced = apply_clahe_lab(img, cfg.clahe_clip_limit, cfg.clahe_grid_size)
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    coords, dx, dy, _ = build_dot_grid(cfg, gray.shape)
    values = process_tiles(gray, coords, cfg)
    if cfg.invert_luminance:
        values = 1.0 - values
    values = enhance_sampled_values(values, cfg)
    values, density_control = apply_density_control(values, cfg)
    method, binary = select_best_dither(values, cfg.dither_candidates)
    binary = correct_over_dense_regions(binary, cfg)
    braille_quality = analyze_braille_quality(binary, cfg)
    tactile_validation = validate_tactile_output(binary, cfg)
    if cfg.mode == 'TACTILE' and bool(getattr(cfg, 'strict_tactile_validation', False)) and not tactile_validation['compliant']:
        raise ValueError('tactile validation failed: ' + json.dumps(tactile_validation['issues'], ensure_ascii=False))
    quality = compute_quality_metrics(values, binary, cfg)
    braille_text = braille_matrix_to_text(encode_to_braille_matrix(binary))
    chromatic_report = None
    if cfg.mode not in ASCII_MODES:
        Path(output_txt).write_text(braille_text, encoding='utf-8')
        if cfg.mode == 'CHROMATIC':
            chromatic_report = render_chromatic_png(binary, img, cfg, output_png)
        else:
            render_braille_png(binary, cfg, output_png)
    svg_report = export_svg(binary, cfg, output_svg) if output_svg is not None else None
    raster_check = raster_roundtrip_check(binary, output_png, cfg) if cfg.mode == 'TACTILE' else {'ok': None, 'skipped': 'non-tactile mode uses antialias/glow/color/text'}
    return {
        'dots_shape': [dy, dx],
        'cells_shape': [dy//4, dx//2],
        'dither_method': method,
        'occupancy_ratio': float(binary.mean()),
        'quality_metrics': quality,
        'tactile_geometry': geometry_report(cfg),
        'tactile_export': svg_report,
        'chromatic_render': chromatic_report,
        'braille_enhancement': {
            'preserve_edges': bool(getattr(cfg, 'braille_preserve_edges', True)),
            'edge_weight': float(getattr(cfg, 'braille_edge_weight', 0.0)),
            'gamma': float(getattr(cfg, 'braille_gamma', 1.0)),
            'contrast': float(getattr(cfg, 'braille_contrast', 1.0)),
        },
        'braille_quality': braille_quality,
        'braille_density_control': density_control,
        'validation': {
            'unicode_roundtrip': unicode_roundtrip_test(),
            'physical_compliance': physical_compliance_check(binary, cfg),
            'tactile_output': tactile_validation,
            'raster_roundtrip': raster_check,
        },
        'diagnostics': {
            'braille_pipeline': {
                'executed': True,
                'reason': 'mode requires Braille dot pipeline' if cfg.mode not in ASCII_MODES else 'include_braille_diagnostics enabled',
            }
        },
    }


def _process_ascii_fast_path(img, cfg: BrailleArtConfig, output_png, output_txt, output_html) -> dict:
    ascii_report = write_ascii_output(img, cfg, output_txt, color=(cfg.mode == 'ASCII_COLOR'), html_path=output_html, png_path=output_png)
    return {
        'dots_shape': None,
        'cells_shape': None,
        'dither_method': None,
        'occupancy_ratio': None,
        'quality_metrics': ascii_report.get('quality', {}),
        'tactile_geometry': geometry_report(cfg),
        'tactile_export': None,
        'chromatic_render': None,
        'ascii_render': ascii_report,
        'braille_enhancement': None,
        'braille_quality': None,
        'braille_density_control': None,
        'validation': {
            'unicode_roundtrip': unicode_roundtrip_test(),
            'physical_compliance': {'ok': None, 'skipped': 'ASCII fast path does not generate tactile dots'},
            'tactile_output': {'compliant': None, 'skipped': 'ASCII fast path does not generate tactile dots'},
            'raster_roundtrip': {'ok': None, 'skipped': 'ASCII preview output is text raster, not tactile dot raster'},
        },
        'diagnostics': {
            'braille_pipeline': {
                'executed': False,
                'reason': 'ASCII mode uses direct text/HTML/PNG preview fast path',
            }
        },
    }


def process_image(image_path, cfg: BrailleArtConfig, output_png='output_braille.png', output_txt='output_braille.txt', report_json='render_report.json', output_svg=None, output_html=None):
    validate_config(cfg)
    start = time.time()
    output_html = _resolve_html_output(cfg, output_txt, output_html)
    _prepare_outputs(output_png, output_txt, report_json, output_svg, output_html)
    img = _load_image(image_path)
    report = _base_report(img, cfg, start, output_png, output_txt, report_json, output_svg, output_html)

    if cfg.mode in ASCII_MODES and not bool(getattr(cfg, 'include_braille_diagnostics', False)):
        mode_report = _process_ascii_fast_path(img, cfg, output_png, output_txt, output_html)
    else:
        mode_report = _process_braille_pipeline(img, cfg, output_png, output_txt, output_svg)
        if cfg.mode in ASCII_MODES:
            mode_report['ascii_render'] = write_ascii_output(img, cfg, output_txt, color=(cfg.mode == 'ASCII_COLOR'), html_path=output_html, png_path=output_png)
        else:
            mode_report.setdefault('ascii_render', None)

    report.update(mode_report)
    report['runtime_sec'] = time.time() - start
    report['renderer'].update({
        'backend': cfg.mode,
        'braille_pipeline_executed': bool(report.get('diagnostics', {}).get('braille_pipeline', {}).get('executed')),
    })
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report
