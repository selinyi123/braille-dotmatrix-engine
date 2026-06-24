import hashlib
import json

from braille_dotmatrix_engine.artifact_provenance import build_artifact_provenance_manifest, main, sha256_file, write_artifact_provenance_manifest


def test_sha256_file(tmp_path):
    target = tmp_path / 'sample.txt'
    target.write_text('abc', encoding='utf-8')
    assert sha256_file(target) == hashlib.sha256(b'abc').hexdigest()


def test_build_artifact_provenance_manifest(tmp_path):
    (tmp_path / 'a.txt').write_text('alpha', encoding='utf-8')
    nested = tmp_path / 'nested'
    nested.mkdir()
    (nested / 'b.txt').write_text('beta', encoding='utf-8')

    manifest = build_artifact_provenance_manifest(tmp_path, label='test-artifact')

    assert manifest['schema'] == 'braille-dotmatrix-engine.artifact_provenance'
    assert manifest['schema_version'] == '1.0'
    assert manifest['label'] == 'test-artifact'
    assert manifest['algorithm'] == 'sha256'
    assert manifest['file_count'] == 2
    assert {item['path'] for item in manifest['files']} == {'a.txt', 'nested/b.txt'}
    assert manifest['total_bytes'] == len('alpha') + len('beta')


def test_write_manifest_excludes_output_file(tmp_path):
    (tmp_path / 'artifact.json').write_text('{"ok": true}', encoding='utf-8')
    output = tmp_path / 'manifest.json'

    manifest = write_artifact_provenance_manifest(tmp_path, output, label='sample')
    persisted = json.loads(output.read_text(encoding='utf-8'))

    assert manifest == persisted
    assert [item['path'] for item in persisted['files']] == ['artifact.json']


def test_cli_writes_manifest(tmp_path):
    (tmp_path / 'artifact.txt').write_text('payload', encoding='utf-8')
    output = tmp_path / 'provenance.json'

    rc = main([str(tmp_path), '--output', str(output), '--label', 'cli-artifact'])

    assert rc == 0
    manifest = json.loads(output.read_text(encoding='utf-8'))
    assert manifest['label'] == 'cli-artifact'
    assert manifest['file_count'] == 1
    assert manifest['files'][0]['path'] == 'artifact.txt'
