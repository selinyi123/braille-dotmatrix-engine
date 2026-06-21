from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .config import BrailleArtConfig
from .renderers import RenderContext, get_renderer
from .schema import PACKAGE_VERSION, RENDER_SCHEMA_VERSION
from .validation import validate_config

ASCII_MODES = {'ASCII_MONO', 'ASCII_COLOR'}


def create_demo_image(path='test_input.png', size=512):
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for x in range(size):
        arr[:, x] = int(255 * x / max(1, size - 1))
    image = Image.fromarray(arr)
    draw = ImageDraw.Draw(image)
    draw.ellipse((size//3, size//3, 2*size//3, 2*size//3), fill=(255, 255, 255))
    draw.text((size//12, size//2), 'BRAILLE', fill=(0, 0, 0))
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
            'strategy': type(get_renderer(cfg.mode)).__name__,
            'braille_diagnostics_requested': bool(getattr(cfg, 'include_braille_diagnostics', False)),
        },
        'artifacts': _artifact_report(output_png, output_txt, report_json, output_svg, output_html),
        'diagnostics': {},
        'config': asdict(cfg),
    }


def process_image(image_path, cfg: BrailleArtConfig, output_png='output_braille.png', output_txt='output_braille.txt', report_json='render_report.json', output_svg=None, output_html=None):
    validate_config(cfg)
    start = time.time()
    output_html = _resolve_html_output(cfg, output_txt, output_html)
    _prepare_outputs(output_png, output_txt, report_json, output_svg, output_html)

    img = _load_image(image_path)
    context = RenderContext(
        image_path=image_path,
        output_png=output_png,
        output_txt=output_txt,
        report_json=report_json,
        output_svg=output_svg,
        output_html=output_html,
    )
    renderer = get_renderer(cfg.mode)
    report = _base_report(img, cfg, start, output_png, output_txt, report_json, output_svg, output_html)
    mode_report = renderer.render(img, cfg, context).report

    report.update(mode_report)
    report['runtime_sec'] = time.time() - start
    report['renderer'].update({
        'backend': cfg.mode,
        'strategy': type(renderer).__name__,
        'braille_pipeline_executed': bool(report.get('diagnostics', {}).get('braille_pipeline', {}).get('executed')),
    })
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report
