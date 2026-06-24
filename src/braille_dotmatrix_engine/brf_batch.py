from __future__ import annotations

import numbers
from pathlib import Path
from typing import Any

from .brf import validate_brf_text
from .embosser import GenericEmbosserProfile

DEFAULT_MAX_BRF_BATCH_FILES = 1000
DEFAULT_MAX_BRF_FILE_BYTES = 2_000_000
DEFAULT_BRF_DIAGNOSTICS_LIMIT = 500


def _positive_int(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f'{name} must be a positive integer')
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f'{name} must be positive')
    return parsed


def resolve_brf_input_paths(root: str | Path, pattern: str = '*.txt', *, max_files: int = DEFAULT_MAX_BRF_BATCH_FILES) -> list[Path]:
    max_files = _positive_int('max_files', max_files)
    root_path = Path(root)
    if root_path.is_file():
        return [root_path]
    if not root_path.exists():
        raise FileNotFoundError(str(root_path))
    files = sorted(path for path in root_path.glob(pattern) if path.is_file())
    if not files:
        raise FileNotFoundError(f'no files matched {pattern} under {root_path}')
    if len(files) > max_files:
        raise ValueError(f'too many BRF input files: {len(files)} exceeds max_files={max_files}')
    return files


def _read_limited_text(path: Path, *, max_file_bytes: int) -> tuple[str, int]:
    max_file_bytes = _positive_int('max_file_bytes', max_file_bytes)
    size = path.stat().st_size
    if size > max_file_bytes:
        raise ValueError(f'BRF input file too large: {path} is {size} bytes, max_file_bytes={max_file_bytes}')
    return path.read_text(encoding='utf-8'), int(size)


def aggregate_brf_file_reports(file_reports: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason: dict[str, int] = {}
    ok_files = 0
    warning_files = 0
    error_files = 0
    warning_count = 0
    error_count = 0
    truncated_files = 0
    total_bytes = 0
    for item in file_reports:
        brf = item['brf_export']
        diagnostics = brf['diagnostics']
        total_bytes += int(item.get('bytes', 0) or 0)
        if diagnostics.get('truncated'):
            truncated_files += 1
        if diagnostics['total'] == 0:
            ok_files += 1
        if brf['warning_count'] > 0:
            warning_files += 1
        if brf['error_count'] > 0:
            error_files += 1
        warning_count += int(brf['warning_count'])
        error_count += int(brf['error_count'])
        for reason, count in diagnostics.get('by_reason', {}).items():
            by_reason[reason] = by_reason.get(reason, 0) + int(count)
    return {
        'total_files': len(file_reports),
        'ok_files': ok_files,
        'warning_files': warning_files,
        'error_files': error_files,
        'issue_files': len(file_reports) - ok_files,
        'warning_count': warning_count,
        'error_count': error_count,
        'by_reason': by_reason,
        'truncated_files': truncated_files,
        'total_bytes': total_bytes,
    }


def validate_brf_files(
    paths: list[Path],
    profile: GenericEmbosserProfile | None = None,
    *,
    strict: bool = False,
    max_file_bytes: int = DEFAULT_MAX_BRF_FILE_BYTES,
    diagnostics_limit: int = DEFAULT_BRF_DIAGNOSTICS_LIMIT,
) -> dict[str, Any]:
    max_file_bytes = _positive_int('max_file_bytes', max_file_bytes)
    diagnostics_limit = _positive_int('diagnostics_limit', diagnostics_limit)
    file_reports: list[dict[str, Any]] = []
    for path in paths:
        text, size = _read_limited_text(Path(path), max_file_bytes=max_file_bytes)
        brf_report = validate_brf_text(text, profile, strict=strict, diagnostics_limit=diagnostics_limit)
        file_reports.append({
            'path': str(path),
            'bytes': size,
            'summary': brf_report['summary'],
            'ok': brf_report['diagnostics']['total'] == 0,
            'warning_count': brf_report['warning_count'],
            'error_count': brf_report['error_count'],
            'diagnostics_truncated': bool(brf_report['diagnostics'].get('truncated')),
            'brf_export': brf_report,
        })
    return {
        'aggregate': aggregate_brf_file_reports(file_reports),
        'files': file_reports,
    }
