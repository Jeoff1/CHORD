# Known Issues

No critical or high-severity blocker remains after Phase 5.

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
4. Existing Phase 4 worship plans and rehearsals are not automatically matched
   to newly created events. Administrators may link them explicitly; unlinked
   schedules remain supported by design.
5. Recurrence and outbound event notifications are not implemented. Current
   events represent individual occurrences.
6. Giving totals and exports are intentionally deferred to Phase 7 reporting.
7. Spotify playback depends on Spotify, the browser, location, account state,
   and third-party cookie/media policies. CHORD provides an ordinary Spotify
   link when embedded playback is unavailable.
8. Browser preview intentionally excludes `.doc` and `.docx`; authorized users
   must download those files. ChordPro support is a safe display subset rather
   than a complete implementation of every directive.

## Resolved

- A reviewed Phase 1-3 baseline Git commit now exists (`6686960`), so the prior
  untracked-repository blocker is closed.

## Design decisions pending

- Account profiles and member records intentionally have separate contact
  fields. No automatic synchronization exists.
- The JSON theme list is structured future input, but taxonomy, recommendation
  behavior, and evaluation belong exclusively to the reserved Phase 8.

No SQLite fallback is configured. See [[Task-Tracker]],
[[../04-Testing/Phase-5-Test-Results]], and
[[../02-Architecture/Architecture-Decisions]].
