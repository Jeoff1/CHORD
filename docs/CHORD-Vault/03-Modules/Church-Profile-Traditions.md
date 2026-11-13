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

## Not yet

Themes (ticket 06): a common list plus each Tradition's own, served by
`services.available_themes()`; songs are tagged from it. Templates, calendar,
and records arrive in tickets 07-13. See [[../01-Project/Phase-7A-Spec]].
