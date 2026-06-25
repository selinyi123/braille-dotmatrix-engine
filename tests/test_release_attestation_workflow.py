from pathlib import Path

WORKFLOW = Path('.github/workflows/release-attestations.yml')


def test_release_attestation_workflow_is_release_scoped():
    content = WORKFLOW.read_text(encoding='utf-8')
    assert 'workflow_dispatch:' in content
    assert 'push:' in content
    assert 'tags:' in content
    assert '"v*"' in content
    assert 'pull_request:' not in content


def test_release_attestation_workflow_uses_minimum_attestation_permissions():
    content = WORKFLOW.read_text(encoding='utf-8')
    assert 'contents: read' in content
    assert 'id-token: write' in content
    assert 'attestations: write' in content
    assert 'packages: write' not in content
    assert 'artifact-metadata: write' not in content


def test_release_attestation_workflow_attests_expected_subjects():
    content = WORKFLOW.read_text(encoding='utf-8')
    assert 'uses: actions/attest@v4' in content
    assert 'subject-path:' in content
    assert 'artifacts/release/*.whl' in content
    assert 'artifacts/release/*.tar.gz' in content
    assert 'artifacts/release/release_attestation_plan.json' in content
    assert 'artifacts/release/release_verification_checklist.json' in content


def test_release_attestation_workflow_generates_verification_checklist():
    content = WORKFLOW.read_text(encoding='utf-8')
    assert 'Generate release verification checklist' in content
    assert 'python -m braille_dotmatrix_engine.release_verification' in content
    assert '--repository selinyi123/braille-dotmatrix-engine' in content
