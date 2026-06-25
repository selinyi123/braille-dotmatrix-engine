import json

from braille_dotmatrix_engine.release_verification import build_release_verification_checklist, main, write_release_verification_checklist


def _plan(artifact_dir='artifacts/release'):
    return {
        'artifact_dir': artifact_dir,
        'subjects': [
            {'path': 'package.whl', 'sha256': 'a' * 64, 'size_bytes': 10},
            {'path': 'brf_batch_report.json', 'sha256': 'b' * 64, 'size_bytes': 20},
        ]
    }


def test_build_release_verification_checklist():
    checklist = build_release_verification_checklist(_plan(), repository='selinyi123/braille-dotmatrix-engine')

    assert checklist['schema'] == 'braille-dotmatrix-engine.release_verification'
    assert checklist['schema_version'] == '1.0'
    assert checklist['repository'] == 'selinyi123/braille-dotmatrix-engine'
    assert checklist['subject_count'] == 2
    assert checklist['checks'][0]['artifact_path'] == 'artifacts/release/package.whl'
    assert checklist['checks'][0]['command'] == 'gh attestation verify artifacts/release/package.whl -R selinyi123/braille-dotmatrix-engine'
    assert checklist['manual_checklist']
    assert 'Offline verification' in checklist['offline_verification_note']


def test_build_release_verification_checklist_uses_plan_artifact_dir():
    checklist = build_release_verification_checklist(_plan('dist/release'), repository='selinyi123/braille-dotmatrix-engine')

    assert checklist['artifact_prefix'] == 'dist/release'
    assert checklist['checks'][0]['artifact_path'] == 'dist/release/package.whl'
    assert checklist['checks'][0]['command'] == 'gh attestation verify dist/release/package.whl -R selinyi123/braille-dotmatrix-engine'


def test_build_release_verification_checklist_allows_prefix_override():
    checklist = build_release_verification_checklist(_plan('dist/release'), repository='selinyi123/braille-dotmatrix-engine', artifact_prefix='downloaded/release')

    assert checklist['artifact_prefix'] == 'downloaded/release'
    assert checklist['checks'][0]['artifact_path'] == 'downloaded/release/package.whl'


def test_write_release_verification_checklist(tmp_path):
    plan_path = tmp_path / 'release_attestation_plan.json'
    output = tmp_path / 'release_verification_checklist.json'
    plan_path.write_text(json.dumps(_plan()), encoding='utf-8')

    checklist = write_release_verification_checklist(plan_path, output, repository='selinyi123/braille-dotmatrix-engine')

    assert json.loads(output.read_text(encoding='utf-8')) == checklist
    assert checklist['subject_count'] == 2


def test_cli_writes_release_verification_checklist(tmp_path):
    plan_path = tmp_path / 'release_attestation_plan.json'
    output = tmp_path / 'release_verification_checklist.json'
    plan_path.write_text(json.dumps(_plan()), encoding='utf-8')

    rc = main([str(plan_path), '--output', str(output), '--repository', 'selinyi123/braille-dotmatrix-engine'])

    assert rc == 0
    checklist = json.loads(output.read_text(encoding='utf-8'))
    assert checklist['checks'][1]['command'] == 'gh attestation verify artifacts/release/brf_batch_report.json -R selinyi123/braille-dotmatrix-engine'
