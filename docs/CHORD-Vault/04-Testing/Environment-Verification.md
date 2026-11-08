# Environment Verification

Last verified: 2026-11-08

| Check | Result |
| --- | --- |
| `.venv` Python | Pass - 3.14.7 |
| Django | Pass - 5.2.19 |
| PostgreSQL | Pass - 17.11, `chord_user` on `chord_db` |
| `pip check` | Pass - no broken requirements |
| Applied migrations | Pass - accounts `0003`, members `0001`, worship `0001` |
| Phase 4 tables | Pass - all 10 present |
| Phase 4 constraints | Pass - reviewed unique and ordering constraints present |
| `manage.py check` | Pass - no issues |
| Migration drift | Pass - no changes detected |
| Full tests | Pass - 69 tests |
| Test database cleanup | Pass |
| Ruff lint | Pass |
| Ruff format | Pass - 70 files formatted |
| Development server | Pass - Phase 4 list routes and redirects verified |
| Secret protection | Pass - `.env` ignored and untracked |
| Resource protection | Pass - files outside public media and permission streamed |

The ordinary development configuration intentionally produces HTTPS-related
`check --deploy` warnings because local development uses HTTP and `DEBUG=True`.
The secure production settings simulation passed during the Phase 1-3 audit;
Phase 4 did not alter that configuration.

Current status: **PHASE 4 COMPLETE.** Phase 5 is not started.

See [[Phase-4-Test-Results]], [[../02-Architecture/Database-Configuration]],
and [[../03-Development/Known-Issues]].
