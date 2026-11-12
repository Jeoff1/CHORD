# Church Profile and Traditions

Phase 7A ticket 01. App: `apps.traditions`. Route: `/church/`.

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
- **Shell**: the header shows "church name · Tradition"; the sidebar shows a
  permission-backed Church profile link.

## Not yet

Terminology, module toggles, tradition roles, songbooks, themes, templates,
calendar, and records arrive in tickets 02-13. See [[../01-Project/Phase-7A-Spec]].
