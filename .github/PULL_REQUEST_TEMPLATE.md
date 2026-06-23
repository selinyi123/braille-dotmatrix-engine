## Summary

- 

## Change type

- [ ] Bug fix
- [ ] Hardening / validation
- [ ] Performance / benchmark
- [ ] Documentation
- [ ] Release

## Agent workflow checklist

- [ ] Audit Agent: failure mode and affected files are identified.
- [ ] Fix Agent: code changes are scoped and minimal.
- [ ] Contract Agent: regression tests or fixtures are included.
- [ ] Performance Agent: resource limits and benchmark impact are considered.
- [ ] Release Gate Agent: CI, package build, and wheel smoke are expected to pass.

## Validation

- [ ] `ruff check .`
- [ ] `pytest -q --cov=braille_dotmatrix_engine --cov-report=term-missing`
- [ ] `python -m build`
- [ ] GitHub Actions benchmark smoke

## Notes

