import pytest

from braille_dotmatrix_engine import (
    GenericEmbosserProfile,
    build_embosser_profile,
    embosser_capacity,
    embosser_export_manifest,
    embosser_profile_names,
    get_embosser_profile_preset,
    validate_embosser_profile,
)


def test_generic_embosser_capacity_report():
    profile = GenericEmbosserProfile(name='unit-a4', page_width_mm=210, page_height_mm=297, margin_left_mm=10, margin_right_mm=10, margin_top_mm=12, margin_bottom_mm=12, cell_width_mm=5, cell_height_mm=9)
    capacity = embosser_capacity(profile)
    assert capacity['profile'] == 'unit-a4'
    assert capacity['cell_mode'] == 'SIX_DOT'
    assert capacity['cols'] == 38
    assert capacity['rows'] == 30


def test_embosser_manifest_for_six_dot_text_export():
    manifest = embosser_export_manifest(GenericEmbosserProfile(name='six-dot'), output_path='out.brf', source_artifact='out.txt')
    assert manifest['ok'] is True
    assert manifest['encoding_family'] == 'BRF_OR_BRAILLE_ASCII'
    assert manifest['portable_text_export'] is True


def test_invalid_embosser_profile_reports_issues_without_capacity():
    manifest = embosser_export_manifest(GenericEmbosserProfile(name='bad', max_cols=10.5))
    assert manifest['ok'] is False
    assert manifest['capacity'] is None
    assert any('max_cols' in issue for issue in manifest['issues'])


def test_invalid_embosser_capacity_raises():
    with pytest.raises(ValueError, match='max_cols'):
        embosser_capacity(GenericEmbosserProfile(max_cols=10.5))


def test_embosser_profile_rejects_non_finite_dimensions():
    issues = validate_embosser_profile(GenericEmbosserProfile(page_width_mm=float('inf')))
    assert any('page_width_mm' in issue for issue in issues)


def test_profile_preset_names_are_stable():
    names = embosser_profile_names()
    assert 'a4-40x25' in names
    assert 'letter-40x25' in names
    assert 'portable-34x25' in names


def test_profile_preset_override_capacity():
    profile = build_embosser_profile('letter-40x25', max_cols=32, max_rows=12)
    capacity = embosser_capacity(profile)
    assert profile.name == 'letter-40x25+override'
    assert capacity['cols'] == 32
    assert capacity['rows'] == 12


def test_profile_preset_override_rejects_fractional_capacity():
    with pytest.raises(ValueError, match='max_cols'):
        build_embosser_profile('letter-40x25', max_cols=32.5)


def test_unknown_profile_preset_is_rejected():
    with pytest.raises(ValueError):
        get_embosser_profile_preset('unknown-profile')
