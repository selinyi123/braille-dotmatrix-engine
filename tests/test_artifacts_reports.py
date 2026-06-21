from braille_dotmatrix_engine import BrailleArtConfig, artifact_manifest, create_demo_image, process_image


def test_artifact_manifest_entry_details(tmp_path):
    manifest = artifact_manifest(
        tmp_path / 'out.png',
        tmp_path / 'out.txt',
        tmp_path / 'report.json',
        tmp_path / 'out.svg',
        tmp_path / 'out.html',
        tmp_path / 'out.brf',
    )
    assert manifest['png']['kind'] == 'image'
    assert manifest['png']['mime'] == 'image/png'
    assert manifest['txt']['kind'] == 'text'
    assert manifest['txt']['mime'] == 'text/plain'
    assert manifest['report_json']['mime'] == 'application/json'
    assert manifest['svg']['mime'] == 'image/svg+xml'
    assert manifest['html']['mime'] == 'text/html'
    assert manifest['brf']['kind'] == 'text'
    assert manifest['brf']['mime'] == 'application/x-brf'
    assert manifest['brf']['exists'] is False


def test_process_image_report_versions(tmp_path):
    image = create_demo_image(tmp_path / 'demo.png', size=96)
    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode='ASCII_MONO', ascii_html=True),
        tmp_path / 'out.png',
        tmp_path / 'ascii.txt',
        tmp_path / 'report.json',
    )
    assert report['package_version']
    assert report['schema_version'] == '1.11'
    assert report['renderer']['strategy'] == 'AsciiMonoRenderer'
    assert report['artifact_manifest']['png']['exists'] is True
    assert report['artifact_manifest']['txt']['exists'] is True
    assert report['artifact_manifest']['brf']['path'] is None
