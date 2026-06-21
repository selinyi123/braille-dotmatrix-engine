from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from braille_dotmatrix_engine.config import BrailleArtConfig


@dataclass(frozen=True)
class RenderContext:
    image_path: str | Path
    output_png: str | Path
    output_txt: str | Path
    report_json: str | Path
    output_svg: str | Path | None = None
    output_html: str | Path | None = None


@dataclass(frozen=True)
class RenderResult:
    report: dict[str, Any]


class Renderer(Protocol):
    mode: str

    def render(self, image_bgr: np.ndarray, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        ...


class BaseRenderer:
    mode = "BASE"

    def render(self, image_bgr: np.ndarray, cfg: BrailleArtConfig, context: RenderContext) -> RenderResult:
        raise NotImplementedError
