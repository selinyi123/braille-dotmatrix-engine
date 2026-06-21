from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifacts import artifact_manifest, legacy_artifact_paths
from .braille_unicode import BRAILLE_BASE, decode_braille_cell
from .embosser import GenericEmbosserProfile, assert_embosser_profile, embosser_capacity

# Braille ASCII glyphs indexed by the Unicode Braille mask U+2800..U+283F.
# This is intentionally limited to six-dot cells. Dots 7 and 8 are rejected by
# the exporter instead of being silently dropped.
BRAILLE_ASCII_BY_MASK = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
BRAILLE_ASCII_BY_CHAR = {chr(BRAILLE_BASE + idx): glyph for idx, glyph in enumerate(BRAILLE_ASCII_BY_MASK)}
BRF_ERROR_REASONS = {'dots_7_or_8_not_supported', 'unsupported_braille_cell'}
BRF_WARNING_REASONS = {'non_braille_character'}


@dataclass(frozen=True)
class BrfExportResult:
    text: str
    report: dict[str, Any]


class BrfExportError(ValueError):
    def __init__(self, report: dict[str, Any]):
        super().__init__('BRF export failed validation')
        self.report = report


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


def brf_issue_severity(reason: str) -> str:
    if reason in BRF_ERROR_REASONS:
        return 'error'
    if reason in BRF_WARNING_REASONS:
        return 'warning'
    return 'warning'


def summarize_brf_diagnostics(unsupported: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason: dict[str, int] = {}
    by_severity: dict[str, int] = {'warning': 0, 'error': 0}
    for item in unsupported:
        reason = str(item.get('reason', 'unknown'))
        severity = str(item.get('severity') or brf_issue_severity(reason))
        by_reason[reason] = by_reason.get(reason, 0) + 1
        if severity not in by_severity:
            by_severity[severity] = 0
        by_severity[severity] += 1
    return {
        'total': len(unsupported),
        'warning_count': by_severity.get('warning', 0),
        'error_count': by_severity.get('error', 0),
        'by_reason': by_reason,
        'by_severity': by_severity,
        'has_errors': by_severity.get('error', 0) > 0,
        'has_warnings': by_severity.get('warning', 0) > 0,
    }


def brf_report_summary(report: dict[str, Any]) -> str:
    diagnostics = report.get('diagnostics', {})
    reasons = diagnostics.get('by_reason', {}) or {}
    reason_text = ','.join(f'{key}:{value}' for key, value in sorted(reasons.items())) or 'none'
    status = 'issues' if int(diagnostics.get('total', 0) or 0) > 0 else 'ok'
    return (
        f"BRF {status}; profile={report.get('profile')}; pages={report.get('pages')}; "
        f"cols={report.get('cols')}; rows={report.get('rows')}; "
        f"warnings={report.get('warning_count', 0)}; errors={report.get('error_count', 0)}; reasons={reason_text}"
    )


def unicode_braille_to_brf_text(text: str, profile: GenericEmbosserProfile | None = None, *, strict: bool = False) -> BrfExportResult:
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
            severity = brf_issue_severity(reason)
            unsupported.append({'line': row_idx + 1, 'column': col_idx + 1, 'char': ch, 'codepoint': f'U+{code:04X}', 'reason': reason, 'severity': severity})
            out_chars.append('?')
        converted_lines.extend(_line_chunks(''.join(out_chars), cols))

    brf_text, pages = _paginate(converted_lines, rows)
    diagnostics = summarize_brf_diagnostics(unsupported)
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
        'strict': strict,
        'validate_only': False,
        'unsupported_count': len(unsupported),
        'warning_count': diagnostics['warning_count'],
        'error_count': diagnostics['error_count'],
        'diagnostics': diagnostics,
        'unsupported': unsupported,
        'ok': diagnostics['error_count'] == 0 and (not strict or diagnostics['total'] == 0),
    }
    report['summary'] = brf_report_summary(report)
    if strict and diagnostics['total'] > 0:
        raise BrfExportError(report)
    return BrfExportResult(text=brf_text, report=report)


def validate_brf_text(text: str, profile: GenericEmbosserProfile | None = None, *, strict: bool = False) -> dict[str, Any]:
    try:
        result = unicode_braille_to_brf_text(text, profile, strict=strict)
        report = dict(result.report)
    except BrfExportError as exc:
        report = dict(exc.report)
    report['validate_only'] = True
    report['path'] = None
    report['bytes'] = 0
    report['summary'] = brf_report_summary(report)
    return report


def write_brf_text(text: str, path: str | Path, profile: GenericEmbosserProfile | None = None, *, strict: bool = False) -> dict[str, Any]:
    result = unicode_braille_to_brf_text(text, profile, strict=strict)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.text, encoding='ascii', newline='\n')
    report = dict(result.report)
    report['path'] = str(path)
    report['bytes'] = path.stat().st_size
    report['summary'] = brf_report_summary(report)
    return report


def attach_brf_artifact_to_report(
    report: dict[str, Any],
    *,
    output_brf: str | Path | None,
    output_png=None,
    output_txt=None,
    report_json=None,
    output_svg=None,
    output_html=None,
    brf_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    updated = dict(report)
    output_png = output_png if output_png is not None else report.get('artifacts', {}).get('png')
    output_txt = output_txt if output_txt is not None else report.get('artifacts', {}).get('txt')
    report_json = report_json if report_json is not None else report.get('artifacts', {}).get('report_json')
    output_svg = output_svg if output_svg is not None else report.get('artifacts', {}).get('svg')
    output_html = output_html if output_html is not None else report.get('artifacts', {}).get('html')
    manifest = artifact_manifest(output_png, output_txt, report_json, output_svg, output_html, output_brf)
    updated['artifact_manifest'] = manifest
    updated['artifacts'] = legacy_artifact_paths(manifest)
    if brf_report is not None:
        updated['brf_export'] = brf_report
    return updated
