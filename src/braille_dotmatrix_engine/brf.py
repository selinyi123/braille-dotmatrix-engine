from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .braille_unicode import BRAILLE_BASE, decode_braille_cell
from .embosser import GenericEmbosserProfile, assert_embosser_profile, embosser_capacity

# Braille ASCII glyphs indexed by the Unicode Braille mask U+2800..U+283F.
# This is intentionally limited to six-dot cells. Dots 7 and 8 are rejected by
# the exporter instead of being silently dropped.
BRAILLE_ASCII_BY_MASK = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
BRAILLE_ASCII_BY_CHAR = {chr(BRAILLE_BASE + idx): glyph for idx, glyph in enumerate(BRAILLE_ASCII_BY_MASK)}


@dataclass(frozen=True)
class BrfExportResult:
    text: str
    report: dict[str, Any]


def _line_chunks(line: str, cols: int) -> list[str]:
    if cols <= 0:
        raise ValueError('cols must be positive')
    if line == '':
        return ['']
    return [line[i : i + cols] for i in range(0, len(line), cols)]


def _paginate(lines: list[str], rows: int) -> tuple[str, int]:
    if rows <= 0:
        raise ValueError('rows must be positive')
    pages = [lines[i : i + rows] for i in range(0, len(lines), rows)] or [[]]
    return '\f'.join('\n'.join(page) for page in pages), len(pages)


def unicode_braille_to_brf_text(text: str, profile: GenericEmbosserProfile | None = None) -> BrfExportResult:
    profile = profile or GenericEmbosserProfile()
    assert_embosser_profile(profile)
    if profile.cell_mode != 'SIX_DOT':
        raise ValueError('BRF text export requires a SIX_DOT profile')

    capacity = embosser_capacity(profile)
    cols = int(capacity['cols'])
    rows = int(capacity['rows'])
    if cols <= 0 or rows <= 0:
        raise ValueError('BRF export requires positive rows and columns')

    converted_lines: list[str] = []
    unsupported: list[dict[str, Any]] = []
    source_lines = text.splitlines()
    if text.endswith('\n'):
        source_lines.append('')

    for row_idx, line in enumerate(source_lines):
        out_chars: list[str] = []
        for col_idx, ch in enumerate(line):
            if ch == ' ':
                out_chars.append(' ')
                continue
            if ch in BRAILLE_ASCII_BY_CHAR:
                out_chars.append(BRAILLE_ASCII_BY_CHAR[ch])
                continue
            code = ord(ch)
            if BRAILLE_BASE <= code <= BRAILLE_BASE + 255:
                dots = decode_braille_cell(ch)
                reason = 'dots_7_or_8_not_supported' if bool(dots[6] or dots[7]) else 'unsupported_braille_cell'
            else:
                reason = 'non_braille_character'
            unsupported.append({'line': row_idx + 1, 'column': col_idx + 1, 'char': ch, 'codepoint': f'U+{code:04X}', 'reason': reason})
            out_chars.append('?')
        converted_lines.extend(_line_chunks(''.join(out_chars), cols))

    brf_text, pages = _paginate(converted_lines, rows)
    report = {
        'exporter': 'brf_text_export',
        'profile': profile.name,
        'cell_mode': profile.cell_mode,
        'encoding': 'BRAILLE_ASCII_SIX_DOT',
        'cols': cols,
        'rows': rows,
        'source_lines': len(source_lines),
        'output_lines': len(converted_lines),
        'pages': pages,
        'unsupported_count': len(unsupported),
        'unsupported': unsupported,
        'ok': not unsupported,
    }
    return BrfExportResult(text=brf_text, report=report)


def write_brf_text(text: str, path: str | Path, profile: GenericEmbosserProfile | None = None) -> dict[str, Any]:
    result = unicode_braille_to_brf_text(text, profile)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.text, encoding='ascii', newline='\n')
    report = dict(result.report)
    report['path'] = str(path)
    report['bytes'] = path.stat().st_size
    return report
