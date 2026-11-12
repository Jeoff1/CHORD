# Phase 7A Spec: Multi-Tradition Support

Status: **Spec, ready-for-agent.** Not yet published to GitHub Issues (`gh`
is not installed). Once it is, publish to `Jeoff1/CHORD` with the label
`ready-for-agent`. Decisions: [[Multi-Tradition-Support]]. Vocabulary: repo
`GLOSSARY.md`.

## Problem Statement

CHORD is built around one implicit, generic Protestant church: six fixed
roles, an SATB choir, contemporary/gospel/hymn categories, a single "worship
service" event type, and free-string song themes. The adviser requires the
proposal prototype to accommodate multiple Christian traditions, with every
module a Christian church may need present. A Roman Catholic parish, an
Alliance church and an Iglesia Ni Cristo locale cannot currently see their
own terminology, roles, records, calendar or song constraints. The planned
song recommender also has no service theme or season to recommend against.

## Solution

A church administrator chooses the church's **Tradition** on a single
**Church Profile**. The Tradition preset reconfigures CHORD:

- which modules appear and what they are called
- which roles exist
- which **Service Templates** and **Song Slots** a worship plan uses
- which **Songbooks** may supply songs
- which **Themes** are available
- which **Seasons** and **Occasions** fill the **Church Calendar**

A new **Church Records** module holds sacramental and church records, with
record types set per Tradition. Every worship plan carries a required
**Service Theme**. ChordPro chord sheets transpose to the setlist's planned
key. A seed command for each Tradition loads a demo church, so the prototype
can be demonstrated as Catholic, Alliance or INC.

## User Stories

1. As a church administrator, I want to set my church's name and Tradition on a Church Profile, so that CHORD speaks my church's language.
2. As a church administrator, I want to switch the active Tradition, so that I can demonstrate CHORD for different churches.
3. As a church administrator, I want switching Tradition to keep all existing data, so that nothing is lost during a demo.
4. As a church administrator, I want records and options that do not apply to the active Tradition hidden, so that screens stay relevant.
5. As a church administrator, I want to enable or disable modules, so that my church only sees what it uses.
6. As a church administrator, I want each Tradition to start with sensible module defaults, so that setup is minimal.
7. As any user, I want navigation labels to use my Tradition's terms (e.g. "Mass", "Worship Service", "Pagsamba"), so that the system feels native.
8. As any user, I want disabled modules absent from navigation and their URLs refused, so that disabled means disabled.
9. As a church administrator, I want roles defined by my Tradition (e.g. Parish Priest, Senior Pastor, Minister, Head Deacon), so that role names match my church.
10. As a church administrator, I want to assign Tradition roles to users, so that access follows my church's structure.
11. As a church administrator, I want each Tradition role mapped to Django permissions as before, so that access control remains server-enforced.
12. As an existing user, I want my current role assignments migrated to equivalent roles, so that my access is unchanged.
13. As a church administrator, I want roles from an inactive Tradition to grant no access, so that switching Tradition cannot leak permissions.
14. As a worship leader, I want to create a worship plan from a Service Template, so that the setlist follows my service's order.
15. As a worship leader, I want setlist entries to fill named Song Slots (e.g. Entrance, Offertory, Communion, Recessional), so that each song has a liturgical purpose.
16. As a worship leader in a free-form tradition, I want generic slots, so that I am not forced into a liturgy.
17. As a worship leader, I want existing worship plans to keep working without a template, so that historic plans remain valid.
18. As a worship leader, I want to assign each song to a Songbook, so that hymnals and libraries are distinguished.
19. As a worship leader, I want setlists to offer only songs from my Tradition's allowed Songbooks, so that I cannot pick a disallowed song.
20. As an INC choir leader, I want the INC hymnal stored as metadata only (number, title, themes), so that copyrighted content is not hosted.
21. As a Catholic music director, I want copyrighted hymnals also stored as metadata only, so that the parish respects copyright.
22. As a worship leader, I want to pick a required Service Theme for every new worship plan, so that the service has a clear focus.
23. As a worship leader, I want to add an optional sermon title and scripture reference, so that the theme has detail.
24. As a worship leader, I want Themes drawn from a shared common list plus my Tradition's own Themes, so that vocabulary is consistent.
25. As a worship leader, I want songs tagged with the same controlled Themes, so that plans and songs can be matched.
26. As a worship leader, I want existing free-string song themes migrated to controlled Themes where they match, so that past tagging is preserved.
27. As a worship leader, I want unmatched legacy theme strings reported, so that I can tag them by hand.
28. As a church administrator, I want a Church Calendar with Seasons and Occasions per Tradition, so that the church year is visible.
29. As a Catholic user, I want Advent, Christmas, Lent, Easter and Ordinary Time seasons, so that planning follows the liturgical year.
30. As an Alliance user, I want key holidays and church occasions (e.g. a missions conference), so that my calendar fits my church.
31. As an INC user, I want occasions (e.g. the anniversary, Thanksgiving) without liturgical seasons, so that the calendar is accurate for INC.
32. As a church administrator, I want to edit Season and Occasion dates, so that movable dates (e.g. Easter) are correct each year.
33. As a worship leader, I want a worship plan to show the Season its date falls in, so that I plan seasonally.
34. As a church administrator, I want to create Church Records (baptism, confirmation, marriage, dedication, funeral and so on), so that the church keeps official records.
35. As a church administrator, I want Church Record types configured per Tradition, so that only relevant record types appear.
36. As a church administrator, I want records linked to members where possible and to free-text names otherwise, so that non-member records can be kept.
37. As a church administrator, I want Church Records restricted to authorized roles, so that personal data stays confidential.
38. As a church administrator, I want an audit trail of Church Record changes, matching the existing member and contribution audits, so that changes are accountable.
39. As a church administrator, I want to search and filter Church Records by type and date, so that I can find a record quickly.
40. As a choir member, I want a ChordPro chord sheet shown transposed to the setlist's planned key, so that I play in the right key.
41. As a choir member, I want to transpose a chord sheet up or down while viewing it, so that I can practice in my range.
42. As a choir member, I want non-ChordPro resources unchanged, so that previews keep working.
43. As a demo presenter, I want a seed command per Tradition that loads a sample church with members, roles, songs, plans, calendar and records, so that each Tradition demos well.
44. As a developer, I want the seed command to be re-runnable without duplicates, so that demos can be reset.
45. As a Phase 8 developer, I want one service to return a plan's theme, season, allowed songbooks and target slot, so that the recommender has a single input source.

## Implementation Decisions

- **New `traditions` app** owning: Tradition, Church Profile (a singleton), module toggles, tradition terminology, Service Template and Song Slot, Theme (common or tradition-scoped), and Season/Occasion (the Church Calendar).
- **Tradition-config service** (a new seam): one internal interface that answers for the active Tradition: enabled modules, term lookup, roles, service templates and slots, allowed songbooks, themes, and the season for a date. Views, templates (via a context processor) and, later, Phase 8 call only this service. No code branches on tradition names.
- **Presets are data**, loaded for Roman Catholic, Alliance and Iglesia Ni Cristo by a data migration or seed. There are no per-tradition Python modules.
- **Roles:** `Role` gains a Tradition (null means common, e.g. church administrator) and loses the fixed-choices constraint on its code. The permissions mapping is unchanged. The existing six roles migrate as common or Alliance-equivalent roles. Role checks ignore roles whose Tradition is inactive.
- **Module gating:** a single mechanism (a decorator or mixin, plus a navigation filter) refuses disabled-module URLs with a 404 and hides their links. Server-side permission checks remain authoritative.
- **Songbooks:** a new Songbook model. `Song` gains a Songbook FK and a metadata-only flag. Metadata-only songs reject lyric and sheet `SongResource` uploads.
- **Themes:** `Song.themes` JSON migrates to an M2M to Theme, and a management command reports unmatched strings. `WorshipPlan` gains a required Service Theme (for new plans), an optional sermon title and scripture reference, and an optional Service Template.
- **PlanSong** gains an optional Song Slot. Position ordering stays authoritative.
- **Church Calendar:** Season and Occasion, each with a tradition, name and start/end date. The service resolves the season for a date. No lectionary.
- **New `records` app:** Church Record Type (per Tradition) and Church Record (type, date, member FK or free-text name, officiant, place, notes, created_by), with an audit-event model mirroring `MemberAuditEvent`. Access goes through a dedicated permission.
- **ChordPro transposition** extends the Phase 6 ChordPro parser to transpose chord tokens by semitones. The default offset is the planned key minus the song's default key. The viewer can change the offset with a query parameter.
- **Seed command:** `seed_tradition <tradition>`, idempotent.
- **Phase 8 lock respected:** no ranking, similarity or ML code. This phase adds only the data and the config-service query Phase 8 will use.

## Testing Decisions

- Good tests assert behaviour you can observe from outside: HTTP status, rendered terms, visible links, saved data and returned values. They never assert internal structure.
- **Seam 1, the Django test client:**
  - Switching tradition changes terminology and navigation.
  - Disabled modules return 404.
  - Tradition roles grant or deny access, and inactive-tradition roles grant nothing.
  - Church Records CRUD works and stays confidential.
  - A new worship plan requires a Service Theme.
  - Setlist forms filter songs by Songbook.
  - Metadata-only songs refuse resources.
  - ChordPro sheets render transposed.
- **Seam 2, the tradition-config service:**
  - Season for a date per Tradition, including INC returning none.
  - Allowed songbooks.
  - Themes (common plus tradition-specific).
  - Slots per template.
  - Seed command idempotency.
  - Role migration preserving access.
  - Theme migration matching.
- **Prior art:** `apps/worship/tests_phase6.py` (resource security, ChordPro previews), `apps/accounts/tests.py` (role and permission access), `apps/members/tests.py` (audit events).
- The full suite must stay green on PostgreSQL, with Ruff lint and format passing.

## Out of Scope

- Multi-church hosting on one installation (future work).
- Lectionary readings.
- Traditions beyond Roman Catholic, Alliance and Iglesia Ni Cristo.
- MusicXML engraving, uploaded audio, and per-voice-part practice tracks.
- Any Phase 8 recommendation logic (locked until authorized).
- The remaining Phase 7 dashboards and reports (these resume after 7A).
- Lyrics or sheets for copyrighted hymnals.

## Further Notes

- This spec reopens two earlier decisions in [[../02-Architecture/Architecture-Decisions]]: the six fixed role codes and free-string themes. The 2026-11-13 entry reopens both deliberately. It contradicts nothing else there.
- For the proposal: cite hymn copyright under ethics and limitations, and cite multi-church hosting as future work.
- Tickets: 13 tracer-bullet tickets in `.scratch/phase-7a/issues/` (01-13, blockers first). Ticket 01 and ticket 11 can start immediately.
