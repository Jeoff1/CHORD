# Multi-Tradition Support (Phase 7A)

Decided 2026-11-13 in a design grilling session. Status: **Planned, not started.**
Supersedes the generic single-tradition assumption for the remainder of Phase 7.

## Why

The adviser requires CHORD to accommodate multiple Christian traditions, with
every module a Christian church may need present even if one church does not
use it. CHORD is a proposal prototype, not a production multi-church service.

## Traditions in scope

- Roman Catholic
- Alliance (Christian and Missionary Alliance)
- Iglesia Ni Cristo (INC)

## Decisions

1. **Church Profile + Tradition.** One church per installation. A single
   Church Profile names the active **Tradition**, which is switchable (for the
   demo). Multi-church hosting is future work.
2. **Tradition is data, not code.** Each Tradition preset defines:
   - enabled modules and terminology (e.g. service = "Mass" / "Worship
     Service" / "Pagsamba");
   - roles (replacing the six fixed role codes), all still mapped to Django
     permissions;
   - service templates with ordered **song slots** (e.g. Entrance, Offertory,
     Communion, Recessional for Mass);
   - allowed **songbooks**;
   - tradition-specific **themes** on top of a shared common theme list;
   - **Church Calendar** seasons and occasions.
   The church administrator may toggle modules off/on.
3. **Church Records module.** Generic sacramental/church records with
   tradition-configured record types (Catholic: baptism, confirmation, first
   communion, marriage, funeral; Alliance: dedication, water baptism, wedding;
   INC: baptism).
4. **Church Calendar.** Named seasons/occasions with date ranges per
   Tradition. A worship plan derives its season from its date. **No
   lectionary readings.** INC has occasions but no liturgical seasons.
5. **Service theme.** Every worship plan has a required controlled-vocabulary
   theme plus optional free-text sermon title / scripture reference. Song
   themes migrate from free strings to the controlled list.
6. **Songbooks.** Songs belong to songbooks; traditions restrict which are
   allowed. INC hymns and copyrighted Catholic hymnals are **metadata only**
   (number, title, themes) with no lyrics or sheets.
7. **ChordPro transposition.** Chord sheets transpose to the setlist's planned
   key, reusing the Phase 6 ChordPro subset. Full MusicXML engraving and
   per-voice-part audio are out of scope.
8. **Tradition switching** keeps all data and hides non-applicable records.
   A per-tradition seed command loads a demo church.

## Phase 8 inputs (recorded, not authorized)

The recommender centres on the **service theme**: theme match as the primary
signal, a light season boost (none for INC), and candidates filtered to the
tradition's allowed songbooks and the target song slot. ML stays locked until
the user authorizes Phase 8.

## Proposal notes

- Future work: multi-church hosting on one installation.
- Ethics/limitations: hymn copyright; INC and Catholic hymnals stored as
  metadata only.

See [[../02-Architecture/Architecture-Decisions]],
[[../03-Development/Development-Roadmap]], and the repository `GLOSSARY.md`.
