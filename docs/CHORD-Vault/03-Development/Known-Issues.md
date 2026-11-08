# Known Issues

No critical blocker remains for Phase 4.

## Medium

1. Git is initialized, but every project source file remains untracked because
   no baseline commit has been created. Review and commit the Phase 1–3 state
   before substantial Phase 4 work.
2. `UserRole` records retain who assigned a current role and when, but removing
   a role deletes that through row. A durable role-removal audit event is not yet
   implemented. Django admin logging covers admin-site changes only.
3. Login rate limiting is not implemented. Add a reviewed solution before any
   public deployment.

## Low

1. The earlier `venv/` and `db.sqlite3` bootstrap artifacts remain ignored on
   disk and are not used by the configured project.
2. Python 3.12 is not installed; the project uses compatible Python 3.14.7.
3. Bootstrap CSS is loaded from a CDN without an offline/static asset strategy.

## Design decision pending

Account profiles and member records intentionally have separate contact fields.
No automatic synchronization exists; decide the canonical source before a
future workflow needs both.

No SQLite fallback is configured. See [[Task-Tracker]],
[[../04-Testing/Phases-1-3-QA-Audit]], and
[[../02-Architecture/Architecture-Decisions]].
