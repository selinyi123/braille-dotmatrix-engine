from pathlib import Path

import pytest

from braille_dotmatrix_engine import (
    BRAILLE_ASCII_BY_CHAR,
    BRAILLE_ASCII_BY_MASK,
    GenericEmbosserProfile,
    attach_brf_artifact_to_report,
    encode_braille_cell,
    unicode_braille_to_brf_text,
    write_brf_text,
)
from braille_dotmatrix_engine.schema import PACKAGE_VERSION


def test_braille_ascii_mask_table_basics():
    assert len(BRAILLE_ASCII_BY_MASK) == 64
    assert BRAILLE_ASCII_BY_CHAR['⠀'] == ' '
    assert BRAILLE_ASCII_BY_CHAR['⠁'] == 'A'
    assert BRAILLE_ASCII_BY_CHAR['⠃'] == 'B'
    assert BRAILLE_ASCII_BY_CHAR['⠿'] == '='


def test_unicode_braille_to_sixdot_text_basic_mapping():
    text = '⠁⠃ ⠉'
    result = unicode_braille_to_brf_text(text, GenericEmbosserProfile(max_cols=20, max_rows=20))
    assert PACKAGE_VERSION == '1.17.0'
    assert result.text == 'AB C'
    assert result.report['ok'] is True
    assert result.report['encoding'] == 'BRAILLE_ASCII_SIX_DOT'
    assert result.report['unsupported_count'] == 0


def test_sixdot_text_wraps_and_paginates():
    profile = GenericEmbosserProfile(max_cols=3, max_rows=2)
    result = unicode_braille_to_brf_text('⠁⠃⠉⠙⠑⠋⠛', profile)
    assert result.text == 'ABC\nDEF\fG'
    assert result.report['cols'] == 3
    assert result.report['rows'] == 2
    assert result.report['pages'] == 2


def test_eight_dot_cells_are_reported():
    cell = encode_braille_cell([True, False, False, False, False, False, True, False])
    result = unicode_braille_to_brf_text(cell, GenericEmbosserProfile(max_cols=10, max_rows=10))
    assert result.text == '?'
    assert result.report['ok'] is False
    assert result.report['unsupported'][0]['reason'] == 'dots_7_or_8_not_supported'


def test_non_braille_characters_are_reported():
    result = unicode_braille_to_brf_text('A', GenericEmbosserProfile(max_cols=10, max_rows=10))
    assert result.text == '?'
    assert result.report['unsupported'][0]['reason'] == 'non_braille_character'


def test_six_dot_profile_required():
    with pytest.raises(ValueError):
        unicode_braille_to_brf_text('⠁', GenericEmbosserProfile(cell_mode='EIGHT_DOT'))


def test_write_sixdot_text(tmp_path: Path):
    path = tmp_path / 'out.brf'
    report = write_brf_text('⠁⠃', path, GenericEmbosserProfile(max_cols=20, max_rows=20))
    assert path.read_text(encoding='ascii') == 'AB'
    assert report['path'].endswith('out.brf')
    assert report['bytes'] == 2
    assert report['ok'] is True


def test_attach_brf_artifact_to_report(tmp_path: Path):
    brf_path = tmp_path / 'out.brf'
    brf_report = write_brf_text('⠁⠃', brf_path, GenericEmbosserProfile(max_cols=20, max_rows=20))
    report = {
        'artifacts': {
            'png': str(tmp_path / 'out.png'),
            'txt': str(tmp_path / 'out.txt'),
            'report_json': str(tmp_path / 'report.json'),
            'svg': None,
            'html': None,
        }
    }
    updated = attach_brf_artifact_to_report(report, output_brf=brf_path, brf_report=brf_report)
    assert updated['artifacts']['brf'].endswith('out.brf')
    assert updated['artifact_manifest']['brf']['exists'] is True
    assert updated['brf_export']['bytes'] == 2
