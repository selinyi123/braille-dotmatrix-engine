from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactSpec:
    key: str
    path: str | Path | None
    kind: str
    role: str
    mime: str | None = None


def _path_string(path: str | Path | None) -> str | None:
    return None if path is None else str(path)


def _exists(path: str | Path | None) -> bool | None:
    if path is None:
        return None
    return Path(path).exists()


def artifact_manifest(output_png, output_txt, report_json, output_svg=None, output_html=None, output_brf=None) -> dict[str, Any]:
    specs = [
        ArtifactSpec('png', output_png, 'image', 'primary visual or tactile raster', 'image/png'),
        ArtifactSpec('txt', output_txt, 'text', 'copyable text output', 'text/plain'),
        ArtifactSpec('report_json', report_json, 'report', 'machine-readable render report', 'application/json'),
        ArtifactSpec('svg', output_svg, 'vector', 'physical millimeter-space tactile vector export', 'image/svg+xml'),
        ArtifactSpec('html', output_html, 'preview', 'browser-previewable ASCII artifact', 'text/html'),
        ArtifactSpec('brf', output_brf, 'text', 'six-dot Braille ASCII / BRF-like export', 'application/x-brf'),
    ]
    return {
        spec.key: {
            'path': _path_string(spec.path),
            'kind': spec.kind,
            'role': spec.role,
            'mime': spec.mime,
            'exists': _exists(spec.path),
        }
        for spec in specs
    }


def legacy_artifact_paths(manifest: dict[str, Any]) -> dict[str, str | None]:
    return {key: value.get('path') for key, value in manifest.items()}


def prepare_artifact_dirs(*paths) -> None:
    for path in paths:
        if path is not None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
