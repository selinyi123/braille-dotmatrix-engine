from __future__ import annotations

from braille_dotmatrix_engine.ascii_backend import write_ascii_output
from braille_dotmatrix_engine.config import BrailleArtConfig

from .base import BaseRenderer, RenderContext, RenderResult
from .common import render_ascii_fast_path, render_braille_pipeline


class AsciiMonoRenderer(BaseRenderer):
    mode = 'ASCII_MONO'

    def render(self, image_bgr, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        if bool(getattr(cfg, 'include_braille_diagnostics', False)):
            report = render_braille_pipeline(image_bgr, cfg, context)
            report['ascii_render'] = write_ascii_output(image_bgr, cfg, context.output_txt, color=False, html_path=context.output_html, png_path=context.output_png)
            return RenderResult(report)
        return RenderResult(render_ascii_fast_path(image_bgr, cfg, context))


class AsciiColorRenderer(BaseRenderer):
    mode = 'ASCII_COLOR'

    def render(self, image_bgr, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        if bool(getattr(cfg, 'include_braille_diagnostics', False)):
            report = render_braille_pipeline(image_bgr, cfg, context)
            report['ascii_render'] = write_ascii_output(image_bgr, cfg, context.output_txt, color=True, html_path=context.output_html, png_path=context.output_png)
            return RenderResult(report)
        return RenderResult(render_ascii_fast_path(image_bgr, cfg, context))
