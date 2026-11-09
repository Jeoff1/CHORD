# Known Issues

No critical or high-severity blocker remains after Phase 7.3 Milestone 3.

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
3. Bootstrap CSS and Lato are loaded from CDNs without an offline/static asset
   strategy.
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
9. The combined exported `static/assets/CHORD.svg` visual reference is about
   32 MiB and remains untracked. If it is to be retained in Git, review ordinary
   Git versus Git LFS rather than committing it accidentally.
10. Exact Figma navigation icons are not available as durable local assets after
    the Starter MCP limit. Phase 7.2 uses accessible text navigation rather than
    substituting an unapproved icon set.
11. Headless Chrome rendered the exported SVG reference crops with GPU disabled,
    but no automated authenticated application screenshot comparison was run.
    A manual desktop/mobile browser pass remains recommended.
12. The event interface represents existing events as a responsive directory,
    not the Figma week-grid calendar. Resource availability, church service
    requests, and room booking require backend domains before that composition
    can be implemented truthfully.

## Resolved

- A reviewed Phase 1-3 baseline Git commit now exists (`6686960`), so the prior
  untracked-repository blocker is closed.

## Design decisions pending

- Account profiles and member records intentionally have separate contact
  fields. No automatic synchronization exists.
- The JSON theme list is structured future input, but taxonomy, recommendation
  behavior, and evaluation belong exclusively to the reserved Phase 8.
- The Phase 7 Figma design includes booking/payment/receipt workflows, unified
  notifications, volunteer availability, post-service feedback, multi-church
  selection, and advanced practice controls that do not have supporting Django
  domains. They require explicit scope and must not be shipped as static or
  misleading UI.
- The Figma file exposes no design variables for the inspected nodes. Phase 7.2
  codifies local desktop tokens and deliberately keeps the mobile practice
  Inter/amber system isolated as a specialized future experience.
- Only the practice screen has a mobile frame. The desktop sidebar, dense
  tables, and reports need responsive and accessibility specifications before
  implementation.

No SQLite fallback is configured. See [[Task-Tracker]],
[[../04-Testing/Phase-5-Test-Results]], and
[[../02-Architecture/Architecture-Decisions]], and
[[Phase-7-Figma-Design-Audit]].
