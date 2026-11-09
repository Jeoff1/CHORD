# Environment Verification

Last verified: 2026-11-09

| Check | Result |
| --- | --- |
| `.venv` Python | Pass - 3.14.7 |
| Django | Pass - 5.2.19 |
| PostgreSQL | Pass - 17.11, `chord_user` on `chord_db` |
| `pip check` | Pass - no broken requirements |
| Applied migrations | Pass - through ministries `0001`, events `0002`, giving `0001`, worship `0003` |
| Phase 5 tables | Pass - all seven new tables introspected |
| `manage.py check` | Pass - no issues |
| Migration drift | Pass - no changes detected |
| Full tests | Pass - 107 tests in 57.301 seconds |
| Test database cleanup | Pass |
| Ruff lint | Pass |
| Ruff format | Pass - 116 files formatted |
| Development server | Pass - song list and resource preview returned expected HTTP 302 login redirects |
| Secret protection | Pass - `.env` remains ignored and untracked |
| ML boundary | Pass - no ML dependency, algorithm, endpoint, ranking, or UI added |

The ordinary development configuration intentionally produces HTTPS-related
`check --deploy` warnings because local development uses HTTP and `DEBUG=True`.
The secure production settings simulation passed during the Phase 1-3 audit;
Phase 5 did not weaken those settings.

Current status: **PHASE 6 COMPLETE.** Phase 7 is not started. Machine learning
is reserved for Phase 8 and is not started.

See [[Phase-6-Test-Results]], [[../02-Architecture/Database-Configuration]],
and [[../03-Development/Known-Issues]].
