import json

from braille_dotmatrix_engine import BrailleArtConfig, create_demo_image, process_image


def test_report_json_manifest_exists_after_process_image(tmp_path):
    image = create_demo_image(tmp_path / "demo.png", size=96)
    report_json = tmp_path / "report.json"

    report = process_image(
        image,
        BrailleArtConfig(output_width_cells=12, mode="TACTILE"),
        tmp_path / "out.png",
        tmp_path / "out.txt",
        report_json,
    )

    assert report_json.exists()
    assert report["artifact_manifest"]["report_json"]["exists"] is True

    persisted = json.loads(report_json.read_text(encoding="utf-8"))
    assert persisted["artifact_manifest"]["report_json"]["exists"] is True
    assert persisted["artifact_manifest"]["png"]["exists"] is True
    assert persisted["artifact_manifest"]["txt"]["exists"] is True
