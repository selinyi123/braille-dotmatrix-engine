from braille_dotmatrix_engine import BrailleArtConfig, artifact_manifest, create_demo_image, process_image


def test_artifact_manifest_includes_roles_and_legacy_paths(tmp_path):
    png = tmp_path / 'out.png'
    txt = tmp_path / 'out.txt'
    report = tmp_path / 'report.json'
    manifest = artifact_manifest(png, txt, report, None, tmp_path / 'out.html')
    assert manifest['png']['path'].endswith('out.png')
    assert manifest['png']['kind'] == 'image'
    assert manifest['png']['mime'] == 'image/png'
    assert manifest['svg']['path'] is None
    assert manifest['html']['role'] == 'browser-previewable ASCII artifact'


def test_process_image_report_has_manifest_and_legacy_artifacts(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_html=True),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        tmp_path / 'report.json',
    )
    assert report['package_version'] == '1.13.0'
    assert report['schema_version'] == '1.10'
    assert report['artifacts']['png'].endswith('out.png')
    assert report['artifact_manifest']['png']['path'].endswith('out.png')
    assert report['artifact_manifest']['png']['exists'] is True
    assert report['artifact_manifest']['txt']['exists'] is True
    assert report['artifact_manifest']['report_json']['path'].endswith('report.json')
    assert report['artifact_manifest']['html']['path'].endswith('ascii.html')
    assert report['renderer']['strategy'] == 'AsciiMonoRenderer'
