# 12: Seed demo churches per Tradition

**What to build:** A demo presenter runs seed_tradition <tradition> to load a complete sample church: profile, roles, users, members, songbooks, songs, themes, templates, calendar, plans and records. Re-running it creates no duplicates.

**Blocked by:** 02, 03, 04, 05, 06, 07, 08, 09, 10

**Status:** done

- [x] The command supports roman-catholic, alliance and iglesia-ni-cristo
- [x] It is idempotent, tested by running it twice
- [x] Metadata-only songbooks contain no lyrics or sheets
- [x] Seed data contains no secrets and no real personal data
