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
  roles (synchronized after migrate in `accounts/signals.py`, reusing a common
  role's permission set): Roman Catholic Parish Priest / Music Director,
  Alliance Senior Pastor / Head Deacon, Iglesia Ni Cristo Minister / Head
  Deacon. `Role.objects.in_effect()` (common + active Tradition) drives the
  permission backend, `User.has_role`, and the assignable roles on the account
  form; an inactive Tradition's roles grant nothing but stay assigned.

## Not yet

Songbooks, themes, templates,
calendar, and records arrive in tickets 03-13. See [[../01-Project/Phase-7A-Spec]].
