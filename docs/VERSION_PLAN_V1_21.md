# v1.21.0 Version Plan — BRF fixture and report examples

## Status

Implemented in `work-20260621-e`.

## Goals

- Add checked-in BRF example fixtures.
- Cover valid six-dot, eight-dot error, and non-Braille warning cases.
- Document expected compact summary prefixes.
- Add pytest coverage that reads fixtures directly.
- Keep render schema stable at `1.11`.

## Acceptance

- `examples/brf/valid_six_dot.txt` validates with `BRF ok;`.
- `examples/brf/eight_dot_error.txt` validates with `dots_7_or_8_not_supported:1`.
- `examples/brf/non_braille_warning.txt` validates with `non_braille_character:1`.
- CLI preflight can run against a checked-in fixture.
- CI passes on Python 3.10, 3.11, and 3.12.

## Next version

`v1.22.0 — BRF preflight batch mode`

Planned goals:

- Accept multiple text files or a directory of fixtures.
- Emit aggregate totals for ok, warning, and error files.
- Preserve per-file summaries.
- Support CI use over `examples/brf/` and generated artifact folders.
