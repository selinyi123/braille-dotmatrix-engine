# v1.21.0 BRF fixture and report example research

## Scope

This pass focuses on reusable BRF fixtures and report examples. It does not repeat earlier research on image-to-Braille conversion, renderer strategy, embosser profile presets, or text preflight mechanics.

## External findings

- Braille ASCII uses 64 printable ASCII characters to encode all six-dot Braille cells.
- BRF files are commonly distributed as plain Braille ASCII plus spaces, line breaks, and page controls.
- Unicode Braille can encode the full eight-dot range, so fixture coverage should include an eight-dot incompatibility case.
- BrlAPI remains a live device abstraction and is outside this fixture/report layer.
- GitHub searches for reusable BRF fixture suites did not surface a stronger project-specific source than adding a local fixture set.

## Decision

Add a minimal checked-in fixture set:

- `examples/brf/valid_six_dot.txt`
- `examples/brf/eight_dot_error.txt`
- `examples/brf/non_braille_warning.txt`

Each fixture should have a deterministic summary expectation and should be validated by tests.

## Next slice

`v1.22.0` should add batch preflight across multiple fixture or artifact files and aggregate summary output.
