import pytest

from braille_dotmatrix_engine import (
    GenericEmbosserProfile,
    assert_embosser_profile,
    embosser_capacity,
    embosser_encoding_family,
    embosser_export_manifest,
    validate_embosser_profile,
)
from braille_dotmatrix_engine.schema import PACKAGE_VERSION


def test_generic_embosser_capacity_report():
    profile = GenericEmbosserProfile(
        name='unit-a4',
        page_width_mm=210,
        page_height_mm=297,
        margin_left_mm=10,
        margin_right_mm=10,
        margin_top_mm=12,
        margin_bottom_mm=12,
        cell_width_mm=5,
        cell_height_mm=9,
    )
    capacity = embosser_capacity(profile)
    assert capacity['profile'] == 'unit-a4'
    assert capacity['cell_mode'] == 'SIX_DOT'
    assert capacity['cols'] == 38
    assert capacity['rows'] == 30
    assert capacity['cells_per_page'] == 1140


def test_embosser_manifest_for_six_dot_text_export():
    profile = GenericEmbosserProfile(name='six-dot')
    manifest = embosser_export_manifest(profile, output_path='out.brf', source_artifact='out.txt')
    assert PACKAGE_VERSION == '1.14.0'
    assert manifest['ok'] is True
    assert manifest['encoding_family'] == 'BRF_OR_BRAILLE_ASCII'
    assert manifest['portable_text_export'] is True
    assert manifest['device_driver_required'] is False
    assert manifest['output_path'] == 'out.brf'


def test_graphics_mode_requires_driver_boundary():
    profile = GenericEmbosserProfile(name='graphics', cell_mode='GRAPHICS', supports_graphics_mode=True, dpi=300)
    manifest = embosser_export_manifest(profile)
    assert manifest['encoding_family'] == 'DEVICE_SPECIFIC_GRAPHICS_MODE'
    assert manifest['device_driver_required'] is True
    assert manifest['portable_text_export'] is False
    assert manifest['capacity']['dpi'] == 300


def test_invalid_embosser_profile_reports_errors():
    profile = GenericEmbosserProfile(page_width_mm=10, page_height_mm=10, margin_left_mm=6, margin_right_mm=6)
    issues = validate_embosser_profile(profile)
    assert issues
    with pytest.raises(ValueError):
        assert_embosser_profile(profile)


def test_graphics_mode_without_support_is_invalid():
    profile = GenericEmbosserProfile(cell_mode='GRAPHICS', supports_graphics_mode=False)
    assert 'GRAPHICS cell mode requires supports_graphics_mode=True' in validate_embosser_profile(profile)
