from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from .json_utils import dumps_json, write_json
from .schema import PACKAGE_VERSION

PROVENANCE_SCHEMA_VERSION = "1.0"

__all__ = [
    "PROVENANCE_SCHEMA_VERSION",
    "sha256_file",
    "build_artifact_provenance_manifest",
    "write_artifact_provenance_manifest",
]


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(root: Path, pattern: str, exclude: Path | None = None) -> list[Path]:
    files: list[Path] = []
    exclude_resolved = exclude.resolve() if exclude is not None else None
    for path in sorted(root.glob(pattern)):
        if not path.is_file():
            continue
        if exclude_resolved is not None and path.resolve() == exclude_resolved:
            continue
        files.append(path)
    return files


def build_artifact_provenance_manifest(root: str | Path, *, label: str = "artifact-provenance", pattern: str = "**/*", exclude: str | Path | None = None) -> dict[str, Any]:
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(str(root_path))
    if not root_path.is_dir():
        raise NotADirectoryError(str(root_path))
    exclude_path = Path(exclude) if exclude is not None else None
    entries = []
    total_bytes = 0
    for path in _iter_files(root_path, pattern, exclude=exclude_path):
        size = path.stat().st_size
        total_bytes += size
        entries.append({
            "path": path.relative_to(root_path).as_posix(),
            "size_bytes": size,
            "sha256": sha256_file(path),
        })
    return {
        "schema": "braille-dotmatrix-engine.artifact_provenance",
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "package_version": PACKAGE_VERSION,
        "label": label,
        "root": str(root_path),
        "algorithm": "sha256",
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }


def write_artifact_provenance_manifest(root: str | Path, output: str | Path, *, label: str = "artifact-provenance", pattern: str = "**/*") -> dict[str, Any]:
    output_path = Path(output)
    manifest = build_artifact_provenance_manifest(root, label=label, pattern=pattern, exclude=output_path)
    write_json(manifest, output_path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a SHA-256 provenance manifest for artifact files")
    parser.add_argument("root", help="artifact directory to scan")
    parser.add_argument("--output", required=True, help="JSON manifest output path")
    parser.add_argument("--label", default="artifact-provenance", help="human-readable artifact group label")
    parser.add_argument("--pattern", default="**/*", help="glob pattern relative to root")
    args = parser.parse_args(argv)
    manifest = write_artifact_provenance_manifest(args.root, args.output, label=args.label, pattern=args.pattern)
    print(dumps_json(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
