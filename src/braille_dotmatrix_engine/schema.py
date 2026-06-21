from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


def _resolve_package_version() -> str:
    try:
        return version("braille-dotmatrix-engine")
    except PackageNotFoundError:  # pragma: no cover - source-tree fallback.
        return "0.0.0+local"


PACKAGE_VERSION = _resolve_package_version()
RENDER_SCHEMA_VERSION = "1.11"
BENCHMARK_SCHEMA_VERSION = "1.11"

__all__ = ["PACKAGE_VERSION", "RENDER_SCHEMA_VERSION", "BENCHMARK_SCHEMA_VERSION"]
