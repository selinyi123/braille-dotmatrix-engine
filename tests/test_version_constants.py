from braille_dotmatrix_engine.schema import BENCHMARK_SCHEMA_VERSION, PACKAGE_VERSION, RENDER_SCHEMA_VERSION


def test_version_constants_for_current_release():
    assert PACKAGE_VERSION.startswith('1.27')
    assert RENDER_SCHEMA_VERSION == '1.12'
    assert BENCHMARK_SCHEMA_VERSION == '1.12'
