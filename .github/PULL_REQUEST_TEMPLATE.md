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

## Contract migration checklist

Complete this section when checked-in JSON contracts or snapshots change.

- [ ] The generated contract was produced from the documented CLI/API path.
- [ ] `report_diff.json` or equivalent diff was reviewed.
- [ ] A contract migration reason is recorded.
- [ ] Tests and snapshots were updated in the same PR.
- [ ] The change is not hiding an unintended renderer, embosser profile, or schema default change.

## Validation

- [ ] `ruff check .`
- [ ] `pytest -q --cov=braille_dotmatrix_engine --cov-report=term-missing`
- [ ] `python -m build`
- [ ] GitHub Actions benchmark smoke

## Notes
