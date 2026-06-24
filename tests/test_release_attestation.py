import json

from braille_dotmatrix_engine.release_attestation import build_release_attestation_plan, main, write_release_attestation_plan


def test_build_release_attestation_plan_collects_release_subjects(tmp_path):
    (tmp_path / 'package.whl').write_text('wheel', encoding='utf-8')
    (tmp_path / 'package.tar.gz').write_text('sdist', encoding='utf-8')
    (tmp_path / 'brf_batch_report.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'ignored.txt').write_text('ignored', encoding='utf-8')

    plan = build_release_attestation_plan(tmp_path)

    assert plan['schema'] == 'braille-dotmatrix-engine.release_attestation_plan'
    assert plan['workflow'] == 'release-attestations'
    assert plan['trigger_policy'] == 'tags-v-and-workflow-dispatch-only'
    assert plan['subject_count'] == 3
    assert [item['path'] for item in plan['subjects']] == ['brf_batch_report.json', 'package.tar.gz', 'package.whl']
    assert all(len(item['sha256']) == 64 for item in plan['subjects'])


def test_write_release_attestation_plan(tmp_path):
    (tmp_path / 'artifact.whl').write_text('wheel', encoding='utf-8')
    output = tmp_path / 'plan.json'

    plan = write_release_attestation_plan(tmp_path, output, subject_globs=['*.whl'])

    assert plan['subject_count'] == 1
    assert json.loads(output.read_text(encoding='utf-8')) == plan


def test_cli_writes_release_attestation_plan(tmp_path):
    (tmp_path / 'artifact.whl').write_text('wheel', encoding='utf-8')
    output = tmp_path / 'plan.json'

    rc = main([str(tmp_path), '--output', str(output), '--subject-glob', '*.whl'])

    assert rc == 0
    plan = json.loads(output.read_text(encoding='utf-8'))
    assert plan['subject_count'] == 1
    assert plan['subjects'][0]['path'] == 'artifact.whl'
