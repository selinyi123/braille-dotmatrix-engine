from .config import BrailleArtConfig, MaterialProfile, PrinterProfile, TactileGeometry
from .pipeline import create_demo_image, process_image
from .chromatic import build_chromatic_array, render_chromatic_png
from .ascii_backend import ASCII_PRESETS, render_ascii_html, render_ascii_png, render_ascii_text, resolve_ascii_charset, write_ascii_output
from .braille_enhance import enhance_sampled_values
from .braille_quality import analyze_braille_quality, apply_density_control
from .geometry import compensated_dot_radius_mm, dot_radius_report
from .renderers import RenderContext, RenderResult, get_renderer, renderer_names
from .schema import BENCHMARK_SCHEMA_VERSION, PACKAGE_VERSION, RENDER_SCHEMA_VERSION
from .validation import VALID_DITHER_METHODS, VALID_RENDER_MODES, validate_config
from .braille_unicode import (
    BRAILLE_BASE,
    BRAILLE_BIT_LAYOUT,
    braille_matrix_to_text,
    decode_braille_cell,
    decode_braille_matrix,
    encode_braille_cell,
    encode_to_braille_matrix,
    unicode_roundtrip_test,
)

__all__ = [
    'BRAILLE_BASE',
    'BRAILLE_BIT_LAYOUT',
    'BrailleArtConfig',
    'MaterialProfile',
    'PrinterProfile',
    'TactileGeometry',
    'create_demo_image',
    'process_image',
    'build_chromatic_array',
    'render_chromatic_png',
    'ASCII_PRESETS',
    'resolve_ascii_charset',
    'render_ascii_text',
    'render_ascii_html',
    'render_ascii_png',
    'write_ascii_output',
    'enhance_sampled_values',
    'apply_density_control',
    'analyze_braille_quality',
    'compensated_dot_radius_mm',
    'dot_radius_report',
    'RenderContext',
    'RenderResult',
    'get_renderer',
    'renderer_names',
    'PACKAGE_VERSION',
    'RENDER_SCHEMA_VERSION',
    'BENCHMARK_SCHEMA_VERSION',
    'VALID_DITHER_METHODS',
    'VALID_RENDER_MODES',
    'validate_config',
    'encode_braille_cell',
    'decode_braille_cell',
    'encode_to_braille_matrix',
    'decode_braille_matrix',
    'braille_matrix_to_text',
    'unicode_roundtrip_test',
]
