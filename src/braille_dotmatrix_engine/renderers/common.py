from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from braille_dotmatrix_engine.ascii_backend import write_ascii_output
from braille_dotmatrix_engine.braille_enhance import enhance_sampled_values
from braille_dotmatrix_engine.braille_quality import analyze_braille_quality, apply_density_control
from braille_dotmatrix_engine.braille_unicode import braille_matrix_to_text, encode_to_braille_matrix, unicode_roundtrip_test
from braille_dotmatrix_engine.chromatic import render_chromatic_png
from braille_dotmatrix_engine.config import BrailleArtConfig
from braille_dotmatrix_engine.dither import correct_over_dense_regions, select_best_dither
from braille_dotmatrix_engine.metrics import compute_quality_metrics
from braille_dotmatrix_engine.preprocess import apply_clahe_lab
from braille_dotmatrix_engine.raster import physical_compliance_check, raster_roundtrip_check, render_braille_png
from braille_dotmatrix_engine.sampling import build_dot_grid, process_tiles
from braille_dotmatrix_engine.tactile import geometry_report, validate_tactile_output
from braille_dotmatrix_engine.vector import export_svg

from .base import RenderContext

ASCII_MODES = {'ASCII_MONO', 'ASCII_COLOR'}


def render_ascii_fast_path(image_bgr: np.ndarray, cfg: BrailleArtConfig, context: RenderContext) -> dict[str, Any]:
    ascii_report = write_ascii_output(
        image_bgr,
        cfg,
        context.output_txt,
        color=(cfg.mode == 'ASCII_COLOR'),
        html_path=context.output_html,
        png_path=context.output_png,
    )
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


def render_braille_pipeline(image_bgr: np.ndarray, cfg: BrailleArtConfig, context: RenderContext) -> dict[str, Any]:
    enhanced = apply_clahe_lab(image_bgr, cfg.clahe_clip_limit, cfg.clahe_grid_size)
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
        Path(context.output_txt).write_text(braille_text, encoding='utf-8')
        if cfg.mode == 'CHROMATIC':
            chromatic_report = render_chromatic_png(binary, image_bgr, cfg, context.output_png)
        else:
            render_braille_png(binary, cfg, context.output_png)
    svg_report = export_svg(binary, cfg, context.output_svg) if context.output_svg is not None else None
    raster_check = raster_roundtrip_check(binary, context.output_png, cfg) if cfg.mode == 'TACTILE' else {'ok': None, 'skipped': 'non-tactile mode uses antialias/glow/color/text'}
    return {
        'dots_shape': [dy, dx],
        'cells_shape': [dy // 4, dx // 2],
        'dither_method': method,
        'occupancy_ratio': float(binary.mean()),
        'quality_metrics': quality,
        'tactile_geometry': geometry_report(cfg),
        'tactile_export': svg_report,
        'chromatic_render': chromatic_report,
        'ascii_render': None,
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
