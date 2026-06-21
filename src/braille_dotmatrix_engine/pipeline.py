from __future__ import annotations

import json
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .artifacts import prepare_artifact_dirs
from .config import BrailleArtConfig
from .renderers import RenderContext, get_renderer
from .reports import adapt_render_report, base_render_report
from .validation import validate_config

ASCII_MODES = {'ASCII_MONO', 'ASCII_COLOR'}


def create_demo_image(path='test_input.png', size=512):
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for x in range(size):
        arr[:, x] = int(255 * x / max(1, size - 1))
    image = Image.fromarray(arr)
    draw = ImageDraw.Draw(image)
    draw.ellipse((size // 3, size // 3, 2 * size // 3, 2 * size // 3), fill=(255, 255, 255))
    draw.text((size // 12, size // 2), 'BRAILLE', fill=(0, 0, 0))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return str(path)


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


def process_image(image_path, cfg: BrailleArtConfig, output_png='output_braille.png', output_txt='output_braille.txt', report_json='render_report.json', output_svg=None, output_html=None):
    validate_config(cfg)
    start = time.time()
    output_html = _resolve_html_output(cfg, output_txt, output_html)
    prepare_artifact_dirs(output_png, output_txt, report_json, output_svg, output_html)
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
    base = base_render_report(img, cfg, start, output_png, output_txt, report_json, output_svg, output_html)
    rendered = renderer.render(img, cfg, context).report
    report = adapt_render_report(base, rendered, cfg, renderer, start, output_png, output_txt, report_json, output_svg, output_html)
    Path(report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report
