from __future__ import annotations

from .ascii_renderer import AsciiColorRenderer, AsciiMonoRenderer
from .base import Renderer
from .braille_renderers import ChromaticRenderer, ScreenRenderer, TactileRenderer

_RENDERERS: dict[str, Renderer] = {
    TactileRenderer.mode: TactileRenderer(),
    ScreenRenderer.mode: ScreenRenderer(),
    ChromaticRenderer.mode: ChromaticRenderer(),
    AsciiMonoRenderer.mode: AsciiMonoRenderer(),
    AsciiColorRenderer.mode: AsciiColorRenderer(),
}


def get_renderer(mode: str) -> Renderer:
    if mode not in _RENDERERS:
        raise ValueError('Unsupported render mode: ' + str(mode))
    return _RENDERERS[mode]


def renderer_names() -> tuple[str, ...]:
    return tuple(_RENDERERS.keys())
