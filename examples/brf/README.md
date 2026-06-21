# BRF fixtures

These fixtures exercise the six-dot BRF preflight path.

## Files

| File | Purpose | Expected summary prefix |
|---|---|---|
| `valid_six_dot.txt` | Valid six-dot Unicode Braille input | `BRF ok;` |
| `eight_dot_error.txt` | Unicode Braille cell using dot 7 or 8 | `BRF issues;` with `dots_7_or_8_not_supported:1` |
| `non_braille_warning.txt` | Non-Braille text fallback case | `BRF issues;` with `non_braille_character:1` |

## CLI examples

```bash
braille-dotmatrix \
  --brf-preflight examples/brf/valid_six_dot.txt \
  --brf-print-summary \
  --report-json artifacts/valid_six_dot_report.json
```

```bash
braille-dotmatrix \
  --brf-preflight examples/brf/eight_dot_error.txt \
  --strict-brf \
  --brf-print-summary \
  --report-json artifacts/eight_dot_error_report.json
```
