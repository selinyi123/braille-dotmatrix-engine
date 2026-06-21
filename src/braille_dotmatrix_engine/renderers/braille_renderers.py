from __future__ import annotations

from braille_dotmatrix_engine.config import BrailleArtConfig

from .base import BaseRenderer, RenderContext, RenderResult
from .common import render_braille_pipeline


class TactileRenderer(BaseRenderer):
    mode = 'TACTILE'

    def render(self, image_bgr, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        return RenderResult(render_braille_pipeline(image_bgr, cfg, context))


class ScreenRenderer(BaseRenderer):
    mode = 'SCREEN'

    def render(self, image_bgr, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        return RenderResult(render_braille_pipeline(image_bgr, cfg, context))


class ChromaticRenderer(BaseRenderer):
    mode = 'CHROMATIC'

    def render(self, image_bgr, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        return RenderResult(render_braille_pipeline(image_bgr, cfg, context))
