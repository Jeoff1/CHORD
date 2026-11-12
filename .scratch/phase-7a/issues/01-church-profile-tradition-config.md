# 01: Church Profile, Tradition presets, and tradition-config service

**What to build:** A church administrator opens a Church Profile screen, sets the church name and picks a Tradition (Roman Catholic, Alliance or Iglesia Ni Cristo). The active Tradition shows in the app shell. A tradition-config service is the single interface the rest of CHORD uses to ask about the active Tradition.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] New traditions app with Tradition and a singleton Church Profile
- [x] Presets for the three Traditions are loaded as data, not per-tradition code
- [x] Only church administrators can view or change the Church Profile (server-enforced)
- [x] The active Tradition is visible in the shared shell
- [x] The tradition-config service exposes the active Tradition and is tested directly
- [x] Switching Tradition keeps all existing data
- [x] Full suite, Ruff and migrations pass on PostgreSQL
