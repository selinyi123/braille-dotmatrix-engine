from __future__ import annotations

import math
import numbers
from dataclasses import asdict, dataclass, replace
from typing import Literal

EmbosserCellMode = Literal['SIX_DOT', 'EIGHT_DOT', 'GRAPHICS']


@dataclass(frozen=True)
class GenericEmbosserProfile:
    name: str = 'generic-embosser'
    cell_mode: EmbosserCellMode = 'SIX_DOT'
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    margin_left_mm: float = 15.0
    margin_right_mm: float = 15.0
    margin_top_mm: float = 15.0
    margin_bottom_mm: float = 15.0
    cell_width_mm: float = 6.0
    cell_height_mm: float = 10.0
    dot_pitch_mm: float = 2.5
    dpi: int | None = None
    supports_interpoint: bool = False
    supports_graphics_mode: bool = False
    max_cols: int | None = None
    max_rows: int | None = None

    @property
    def printable_width_mm(self) -> float:
        return max(0.0, self.page_width_mm - self.margin_left_mm - self.margin_right_mm)

    @property
    def printable_height_mm(self) -> float:
        return max(0.0, self.page_height_mm - self.margin_top_mm - self.margin_bottom_mm)


EMBOSSER_PROFILE_PRESETS: dict[str, GenericEmbosserProfile] = {
    'a4-40x25': GenericEmbosserProfile(
        name='a4-40x25',
        page_width_mm=210.0,
        page_height_mm=297.0,
        margin_left_mm=10.0,
        margin_right_mm=10.0,
        margin_top_mm=12.0,
        margin_bottom_mm=12.0,
        cell_width_mm=4.7,
        cell_height_mm=10.0,
        max_cols=40,
        max_rows=25,
    ),
    'letter-40x25': GenericEmbosserProfile(
        name='letter-40x25',
        page_width_mm=215.9,
        page_height_mm=279.4,
        margin_left_mm=10.0,
        margin_right_mm=10.0,
        margin_top_mm=12.0,
        margin_bottom_mm=12.0,
        cell_width_mm=4.8,
        cell_height_mm=10.0,
        max_cols=40,
        max_rows=25,
    ),
    'portable-34x25': GenericEmbosserProfile(
        name='portable-34x25',
        page_width_mm=210.0,
        page_height_mm=297.0,
        margin_left_mm=18.0,
        margin_right_mm=18.0,
        margin_top_mm=12.0,
        margin_bottom_mm=12.0,
        cell_width_mm=5.0,
        cell_height_mm=10.0,
        max_cols=34,
        max_rows=25,
    ),
    'a4-interpoint-40x25': GenericEmbosserProfile(
        name='a4-interpoint-40x25',
        page_width_mm=210.0,
        page_height_mm=297.0,
        margin_left_mm=10.0,
        margin_right_mm=10.0,
        margin_top_mm=12.0,
        margin_bottom_mm=12.0,
        cell_width_mm=4.7,
        cell_height_mm=10.0,
        supports_interpoint=True,
        max_cols=40,
        max_rows=25,
    ),
}


def embosser_profile_names() -> list[str]:
    return sorted(EMBOSSER_PROFILE_PRESETS)


def get_embosser_profile_preset(name: str) -> GenericEmbosserProfile:
    try:
        return EMBOSSER_PROFILE_PRESETS[name]
    except KeyError as exc:
        known = ', '.join(embosser_profile_names())
        raise ValueError(f'unknown embosser profile preset: {name}; known presets: {known}') from exc


def build_embosser_profile(name: str = 'a4-40x25', *, max_cols: int | None = None, max_rows: int | None = None) -> GenericEmbosserProfile:
    profile = get_embosser_profile_preset(name)
    max_cols = _optional_positive_int('max_cols', max_cols) if max_cols is not None else None
    max_rows = _optional_positive_int('max_rows', max_rows) if max_rows is not None else None
    if max_cols is not None or max_rows is not None:
        profile = replace(
            profile,
            name=f'{profile.name}+override',
            max_cols=max_cols if max_cols is not None else profile.max_cols,
            max_rows=max_rows if max_rows is not None else profile.max_rows,
        )
    return profile


def _finite(name: str, value) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name} must be finite') from None
    if not math.isfinite(parsed):
        raise ValueError(f'{name} must be finite')
    return parsed


def _optional_positive_int(name: str, value) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f'{name} must be a positive integer when provided')
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f'{name} must be positive when provided')
    return parsed


def _safe_int_capacity(available_mm: float, unit_mm: float) -> int:
    if available_mm <= 0 or unit_mm <= 0:
        return 0
    return int(available_mm // unit_mm)


def embosser_capacity(profile: GenericEmbosserProfile) -> dict[str, int | float | str | bool | None]:
    assert_embosser_profile(profile)
    computed_cols = _safe_int_capacity(profile.printable_width_mm, profile.cell_width_mm)
    computed_rows = _safe_int_capacity(profile.printable_height_mm, profile.cell_height_mm)
    cols = min(computed_cols, int(profile.max_cols)) if profile.max_cols is not None else computed_cols
    rows = min(computed_rows, int(profile.max_rows)) if profile.max_rows is not None else computed_rows
    return {
        'profile': profile.name,
        'cell_mode': profile.cell_mode,
        'printable_width_mm': round(profile.printable_width_mm, 3),
        'printable_height_mm': round(profile.printable_height_mm, 3),
        'computed_cols': computed_cols,
        'computed_rows': computed_rows,
        'cols': cols,
        'rows': rows,
        'cells_per_page': cols * rows,
        'supports_interpoint': profile.supports_interpoint,
        'supports_graphics_mode': profile.supports_graphics_mode,
        'dpi': profile.dpi,
    }


def validate_embosser_profile(profile: GenericEmbosserProfile) -> list[str]:
    issues: list[str] = []
    try:
        page_width = _finite('page_width_mm', profile.page_width_mm)
        page_height = _finite('page_height_mm', profile.page_height_mm)
        margin_left = _finite('margin_left_mm', profile.margin_left_mm)
        margin_right = _finite('margin_right_mm', profile.margin_right_mm)
        margin_top = _finite('margin_top_mm', profile.margin_top_mm)
        margin_bottom = _finite('margin_bottom_mm', profile.margin_bottom_mm)
        cell_width = _finite('cell_width_mm', profile.cell_width_mm)
        cell_height = _finite('cell_height_mm', profile.cell_height_mm)
        dot_pitch = _finite('dot_pitch_mm', profile.dot_pitch_mm)
    except ValueError as exc:
        return [str(exc)]

    if page_width <= 0 or page_height <= 0:
        issues.append('page dimensions must be positive')
    if margin_left < 0 or margin_right < 0 or margin_top < 0 or margin_bottom < 0:
        issues.append('margins must be non-negative')
    if profile.printable_width_mm <= 0 or profile.printable_height_mm <= 0:
        issues.append('printable area must be positive after margins')
    if cell_width <= 0 or cell_height <= 0:
        issues.append('cell dimensions must be positive')
    if dot_pitch <= 0:
        issues.append('dot pitch must be positive')
    if profile.cell_mode not in ('SIX_DOT', 'EIGHT_DOT', 'GRAPHICS'):
        issues.append('cell_mode must be SIX_DOT, EIGHT_DOT, or GRAPHICS')
    if profile.cell_mode == 'GRAPHICS' and not profile.supports_graphics_mode:
        issues.append('GRAPHICS cell mode requires supports_graphics_mode=True')
    for field_name in ('max_cols', 'max_rows', 'dpi'):
        try:
            _optional_positive_int(field_name, getattr(profile, field_name))
        except ValueError as exc:
            issues.append(str(exc))
    return issues


def embosser_encoding_family(profile: GenericEmbosserProfile) -> str:
    if profile.cell_mode == 'SIX_DOT':
        return 'BRF_OR_BRAILLE_ASCII'
    if profile.cell_mode == 'EIGHT_DOT':
        return 'UNICODE_BRAILLE_OR_DEVICE_SPECIFIC_8_DOT'
    return 'DEVICE_SPECIFIC_GRAPHICS_MODE'


def embosser_export_manifest(profile: GenericEmbosserProfile, *, output_path: str | None = None, source_artifact: str | None = None) -> dict:
    issues = validate_embosser_profile(profile)
    capacity = None if issues else embosser_capacity(profile)
    return {
        'exporter': 'generic_embosser_boundary',
        'profile': asdict(profile),
        'encoding_family': embosser_encoding_family(profile),
        'capacity': capacity,
        'output_path': output_path,
        'source_artifact': source_artifact,
        'device_driver_required': profile.cell_mode == 'GRAPHICS' or profile.supports_graphics_mode,
        'portable_text_export': profile.cell_mode == 'SIX_DOT',
        'issues': issues,
        'ok': not issues,
    }


def assert_embosser_profile(profile: GenericEmbosserProfile) -> None:
    issues = validate_embosser_profile(profile)
    if issues:
        raise ValueError('; '.join(issues))
