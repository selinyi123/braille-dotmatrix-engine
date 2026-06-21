from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any

from .artifacts import artifact_manifest, legacy_artifact_paths
from .config import BrailleArtConfig
from .renderers import get_renderer
from .schema import PACKAGE_VERSION, RENDER_SCHEMA_VERSION


def base_render_report(image_bgr, cfg: BrailleArtConfig, start_time: float, output_png, output_txt, report_json, output_svg=None, output_html=None) -> dict[str, Any]:
    h, w = image_bgr.shape[:2]
    manifest = artifact_manifest(output_png, output_txt, report_json, output_svg, output_html)
    return {
        'package_version': PACKAGE_VERSION,
        'schema_version': RENDER_SCHEMA_VERSION,
        'image_shape': [h, w],
        'runtime_sec': time.time() - start_time,
        'seed': cfg.seed,
        'mode': cfg.mode,
        'renderer': {
            'mode': cfg.mode,
            'backend': cfg.mode,
            'strategy': type(get_renderer(cfg.mode)).__name__,
            'braille_diagnostics_requested': bool(getattr(cfg, 'include_braille_diagnostics', False)),
        },
        'artifacts': legacy_artifact_paths(manifest),
        'artifact_manifest': manifest,
        'diagnostics': {},
        'config': asdict(cfg),
    }


def adapt_render_report(base_report: dict[str, Any], renderer_report: dict[str, Any], cfg: BrailleArtConfig, renderer, start_time: float, output_png, output_txt, report_json, output_svg=None, output_html=None) -> dict[str, Any]:
    report = dict(base_report)
    report.update(renderer_report)
    manifest = artifact_manifest(output_png, output_txt, report_json, output_svg, output_html)
    report['runtime_sec'] = time.time() - start_time
    report['artifacts'] = legacy_artifact_paths(manifest)
    report['artifact_manifest'] = manifest
    report.setdefault('diagnostics', {})
    report.setdefault('renderer', {})
    report['renderer'].update({
        'backend': cfg.mode,
        'strategy': type(renderer).__name__,
        'braille_pipeline_executed': bool(report.get('diagnostics', {}).get('braille_pipeline', {}).get('executed')),
    })
    return report
