# Church Profile and Traditions

Phase 7A tickets 01-02. App: `apps.traditions`. Route: `/church/`.

## What exists

- **Tradition**: preset rows loaded by data migration: Alliance,
  Iglesia Ni Cristo, Roman Catholic (codes `alliance`, `iglesia-ni-cristo`,
  `roman-catholic`).
- **Church Profile**: a singleton (pk 1) holding the church name and active
  Tradition. A data migration creates it as "My Church" / Alliance. Admin
  cannot add or delete it.
- **Tradition-config service** (`apps/traditions/services.py`):
  `list_traditions()`, `get_church_profile()`, `get_active_tradition()`. All
  later Phase 7A features ask the active Tradition through this service only.
- **Church Profile screen**: church administrators change the name and
  Tradition. Requires `traditions.manage_church_profile` and
  `traditions.change_churchprofile`. Switching keeps all data.
- **Terminology** (ticket 02): each Tradition preset stores `terminology`
  (e.g. `service` = Worship Service / Pagsamba / Mass). `services.terms()` and
  `services.term(key)` read it; templates get `tradition_terms`. Service-plan
  navigation, breadcrumb and headings use it.
- **Module toggles** (ticket 02): gateable modules are the URL namespaces
  `members`, `ministries`, `events`, `giving`, `worship`
  (`services.MODULES`). Presets ship `default_modules` (all enabled today);
  the Church Profile stores only `module_overrides`, which persist across a
  Tradition switch. Administrators toggle modules on the Church Profile screen.
- **Module gating**: `ModuleGateMiddleware` returns 404 for every URL in a
  disabled module's namespace. The context processor replaces template `perms`
  with a module-scoped wrapper, so permission-gated links to disabled modules
  disappear everywhere; the dashboard uses `ModuleScopedPerms`. Views keep
  their own permission checks, which stay authoritative.
- **Shell**: the header shows "church name · Tradition"; the sidebar shows a
  permission-backed Church profile link.

- **Tradition roles** (ticket 03): `Role.tradition` is optional; empty means a
  common role. The six original roles stay common. Presets add their own
  roles (defined in the `traditions/roles.py` catalogue, synchronized after
  migrate by `accounts/signals.py`, reusing a common role's permission set): Roman Catholic Parish Priest / Music Director,
  Alliance Senior Pastor / Head Deacon, Iglesia Ni Cristo Minister / Head
  Deacon. `Role.objects.in_effect()` (common + active Tradition) drives the
  permission backend and the assignable roles on the account form
  (`services.roles_in_effect()`, `services.users_with_permission()`); an inactive Tradition's roles grant nothing but stay assigned.

- **Songbooks** (ticket 05): `worship.Songbook` (code, name, `metadata_only`,
  M2M `traditions`). Presets: General Library (Alliance, Roman Catholic),
  Catholic Hymnal (Roman Catholic, metadata only), INC Hymnal (Iglesia Ni
  Cristo, metadata only). `Song.songbook` is required (existing songs migrated
  to General Library); a blank song-form choice falls back to the Tradition's
  first allowed full-content songbook (metadata-only books sort last). `Song.metadata_only` marks a single song.
  `services.allowed_songbooks()` limits setlist song choices server-side.
  Songs where `is_metadata_only` is true refuse lyrics, chord-sheet and
  lead-sheet `SongResource`s (file or link); reference audio is still allowed.
- **Demo churches** (ticket 12): `python manage.py seed_tradition
  <roman-catholic|alliance|iglesia-ni-cristo> [--password ...]` loads a
  fictional church (profile, role-holding users, members, songs tagged with
  Themes, plans filling Song Slots, Church Records) from
  `apps/traditions/demo.py` and makes that Tradition active. Presets (Themes,
  templates, calendar, record types, songbooks) come from migrations. It is
  idempotent (keyed by username, member name, song title + songbook, plan
  title, record type + member + date). Accounts get unusable passwords unless
  `--password` is given; emails use `example.com`; metadata-only songbooks get
  titles only (INC uses placeholder titles). It refuses a database whose
  Church Profile has a non-demo name or that has non-demo members, unless
  `--force` is given. Seeding another Tradition keeps earlier demo data.

## Not yet

Themes (ticket 06): a common list plus each Tradition's own, served by
`services.available_themes()`; songs are tagged from it, and each new
worship plan picks a required Service Theme from it (ticket 07). Service Templates
(ticket 08): each preset has templates with ordered Song Slots (Mass; Worship
Service; Pagsamba), served by `services.available_service_templates()`.
Church Calendar (ticket 09): `traditions.Season` and `traditions.Occasion`
(Tradition, name, inclusive start/end date) seeded for the 2026-27 church year
(Catholic seasons; Alliance holidays and occasions; INC occasions only).
`services.season_for(date)` resolves the active Tradition's Season (none for
INC); `/church/calendar/` lists entries and lets church administrators edit
dates for movable feasts. No lectionary. Phase 8 inputs (ticket 13): `services.slot_context(plan,
song_slot)` returns a `SlotContext` with the plan's Service Theme, derived
Season, allowed Songbooks and target Song Slot in one call; it raises
`ValueError` for a slot outside the plan's Service Template. It holds context
only: no ranking or similarity. Church Records (ticket 10) live in
the separate `records` app and gateable module; see the Development Log. See [[../01-Project/Phase-7A-Spec]].
