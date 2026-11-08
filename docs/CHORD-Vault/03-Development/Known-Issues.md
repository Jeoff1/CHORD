# Known Issues

No critical or high-severity blocker remains after Phase 4.

## Medium

1. `UserRole` retains who assigned a current role and when, but removing a role
   deletes the through row. A durable role-removal audit event is not yet
   implemented. Django admin logging covers admin-site changes only.
2. Login rate limiting is not implemented. Add a reviewed solution before any
   public deployment.
3. Uploaded song resources enforce authorization metadata, extension allowlists,
   a 10 MiB limit, protected storage, and authenticated streaming, but malware
   scanning is not implemented. Add scanning before accepting untrusted public
   uploads.

## Low

1. The earlier `venv/` and `db.sqlite3` bootstrap artifacts remain ignored on
   disk and are not used by the configured project.
2. Python 3.12 is not installed; the project uses compatible Python 3.14.7.
3. Bootstrap CSS is loaded from a CDN without an offline/static asset strategy.
4. Worship plans carry their own service date, location, and status because no
   church-wide event module exists. Add an explicit event relationship only
   when that later module is implemented; do not duplicate event records now.

## Resolved

- A reviewed Phase 1-3 baseline Git commit now exists (`6686960`), so the prior
  untracked-repository blocker is closed.

## Design decisions pending

- Account profiles and member records intentionally have separate contact
  fields. No automatic synchronization exists.
- The JSON theme list is structured recommendation input, but the future ML
  feature still needs an approved taxonomy and evaluation plan.

No SQLite fallback is configured. See [[Task-Tracker]],
[[../04-Testing/Phase-4-Test-Results]], and
[[../02-Architecture/Architecture-Decisions]].
