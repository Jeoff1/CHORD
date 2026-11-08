# Environment Verification

Last verified: 2026-11-07

| Check | Result |
| --- | --- |
| `.venv` Python | Pass — 3.14.7 |
| Django | Pass — 5.2.19 |
| PostgreSQL | Pass — 17.11, `chord_user` on `chord_db` |
| `pip check` | Pass — no broken requirements |
| Applied migrations | Pass — accounts through `0003`, members through `0001` |
| Required tables | Pass |
| Constraints and indexes | Pass — all reviewed constraints/indexes present |
| `manage.py check` | Pass — no issues |
| Migration drift | Pass — no changes detected |
| Full tests | Pass — 44 tests |
| Test database cleanup | Pass |
| Ruff lint | Pass |
| Ruff format | Pass — 56 files already formatted |
| Secure `check --deploy` simulation | Pass — no issues |
| Development server | Pass — login 200 and protected-route redirects |
| Secret protection | Pass — `.env` ignored and untracked |

The ordinary development configuration intentionally produces HTTPS-related
`check --deploy` warnings because local development uses HTTP and `DEBUG=True`.
When secure production environment flags were supplied, the deployment check
reported no issues.

Final audit status: **READY FOR PHASE 4.**

See [[Phases-1-3-QA-Audit]], [[../02-Architecture/Database-Configuration]], and
[[../03-Development/Known-Issues]].
