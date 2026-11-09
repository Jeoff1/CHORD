# Phase 6 Test Results

Verified: **2026-11-09**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| `manage.py migrate` | Pass - `worship.0003` applied |
| Full Django suite | Pass - 107 tests in 57.301 seconds |
| Phase 6 tests | Pass - 13 tests |
| PostgreSQL test database cleanup | Pass |
| `pip check` | Pass - no broken requirements |
| `ruff check .` | Pass |
| `ruff format --check .` | Pass - 116 files formatted |
| Development server | Pass - protected route redirect verified |

## Phase 6 coverage

- Accepted raw, URI, standard, localized, and embed Spotify track forms
- Rejected HTTP, other-host, album, malformed-port, wrong-type, and short IDs
- Normalized storage and official embed rendering
- Protected PDF inline response and unauthorized HTTP 403
- Autoescaped text preview and structured ChordPro rendering
- Unsupported Word-file fallback
- Authorized resource replacement, updater metadata, and post-commit old-file
  cleanup
- Choir Member resource-update denial
- Resource visibility through worship plans, assignments, and rehearsals

All 94 Phase 1-5 tests passed unchanged. No ML behavior or dependency was
introduced.
