from .config import BrailleArtConfig, MaterialProfile, PrinterProfile, TactileGeometry
from .pipeline import create_demo_image, process_image
from .chromatic import build_chromatic_array, render_chromatic_png
from .ascii_backend import ASCII_PRESETS, render_ascii_html, render_ascii_png, render_ascii_text, resolve_ascii_charset, write_ascii_output
from .artifacts import artifact_manifest, legacy_artifact_paths, prepare_artifact_dirs
from .artifact_provenance import PROVENANCE_SCHEMA_VERSION, build_artifact_provenance_manifest, sha256_file, write_artifact_provenance_manifest
from .brf import BRAILLE_ASCII_BY_CHAR, BRAILLE_ASCII_BY_MASK, BrfExportResult, attach_brf_artifact_to_report, unicode_braille_to_brf_text, write_brf_text
from .brf_contract import batch_contract_from_report, write_batch_contract_from_report
from .contract_migration import CONTRACT_MIGRATION_SCHEMA_VERSION, propose_contract_migration, write_contract_migration
from .embosser import (
    EMBOSSER_PROFILE_PRESETS,
    GenericEmbosserProfile,
    assert_embosser_profile,
    build_embosser_profile,
    embosser_capacity,
    embosser_encoding_family,
    embosser_export_manifest,
    embosser_profile_names,
    get_embosser_profile_preset,
    validate_embosser_profile,
)
from .braille_enhance import enhance_sampled_values
from .braille_quality import analyze_braille_quality, apply_density_control
from .geometry import compensated_dot_radius_mm, dot_radius_report
from .release_attestation import RELEASE_ATTESTATION_PLAN_SCHEMA_VERSION, build_release_attestation_plan, write_release_attestation_plan
from .release_verification import RELEASE_VERIFICATION_SCHEMA_VERSION, build_release_verification_checklist, write_release_verification_checklist
from .renderers import RenderContext, RenderResult, get_renderer, renderer_names
from .report_diff import diff_reports, summarize_diff
from .report_diff_policy import REPORT_DIFF_POLICY_SCHEMA_VERSION, evaluate_report_diff_policy, write_report_diff_policy
from .reports import adapt_render_report, base_render_report
from .schema import BENCHMARK_SCHEMA_VERSION, BRF_SCHEMA_VERSION, PACKAGE_VERSION, RENDER_SCHEMA_VERSION
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
    'artifact_manifest',
    'legacy_artifact_paths',
    'prepare_artifact_dirs',
    'PROVENANCE_SCHEMA_VERSION',
    'sha256_file',
    'build_artifact_provenance_manifest',
    'write_artifact_provenance_manifest',
    'BRAILLE_ASCII_BY_CHAR',
    'BRAILLE_ASCII_BY_MASK',
    'BrfExportResult',
    'attach_brf_artifact_to_report',
    'unicode_braille_to_brf_text',
    'write_brf_text',
    'batch_contract_from_report',
    'write_batch_contract_from_report',
    'CONTRACT_MIGRATION_SCHEMA_VERSION',
    'propose_contract_migration',
    'write_contract_migration',
    'EMBOSSER_PROFILE_PRESETS',
    'GenericEmbosserProfile',
    'build_embosser_profile',
    'embosser_capacity',
    'embosser_encoding_family',
    'embosser_export_manifest',
    'embosser_profile_names',
    'get_embosser_profile_preset',
    'validate_embosser_profile',
    'assert_embosser_profile',
    'enhance_sampled_values',
    'apply_density_control',
    'analyze_braille_quality',
    'compensated_dot_radius_mm',
    'dot_radius_report',
    'RELEASE_ATTESTATION_PLAN_SCHEMA_VERSION',
    'build_release_attestation_plan',
    'write_release_attestation_plan',
    'RELEASE_VERIFICATION_SCHEMA_VERSION',
    'build_release_verification_checklist',
    'write_release_verification_checklist',
    'RenderContext',
    'RenderResult',
    'get_renderer',
    'renderer_names',
    'diff_reports',
    'summarize_diff',
    'REPORT_DIFF_POLICY_SCHEMA_VERSION',
    'evaluate_report_diff_policy',
    'write_report_diff_policy',
    'adapt_render_report',
    'base_render_report',
    'PACKAGE_VERSION',
    'RENDER_SCHEMA_VERSION',
    'BRF_SCHEMA_VERSION',
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
