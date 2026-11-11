# Choir and Worship Management

Status: **Completed - Phase 4 (2026-11-08)**

## Choir management

- One choir enrollment per existing member record
- Voice part, active/on-leave/inactive status, join date, and notes
- Choir Leader and Church Administrator roster management
- Rehearsal schedule with validation, location, status, and notes
- Unique per-member rehearsal attendance with recorder metadata
- Audience-scoped announcements with publication and expiry times
- Participant dashboard for upcoming rehearsals, announcements, and own song
  assignments

Choir enrollment is intentionally distinct from a Choir Member account role.
The former is domain participation; the latter grants application access.

## Worship song library

- Title, artist, default key, 20-300 BPM tempo, category, notes, and UUID
- Normalized, deduplicated, bounded JSON worship-theme metadata
- Search by title/artist, category and theme filters, and allowlisted sorting
- Usage history derived from worship-plan setlists
- Chord sheets, lead sheets, lyrics, and reference resources
- Exactly one uploaded file or external URL per resource
- Required license/permission/source reference
- Extension allowlist, 10 MiB size limit, protected storage, and
  permission-checked file streaming

The theme metadata prepares a clean future input but does not contain a
recommendation algorithm, embedding, model, score, or ML dependency.

## Worship planning

- Service title, time, location, preparation notes, and draft/preparing/ready/
  completed/cancelled status
- Active choir participation managed through an explicit through model
- Ordered setlists with planned key and notes
- Transactional add, move, and remove operations with row locking
- Song assignments limited to choir participants in that plan
- Assignment cleanup when a participant is removed
- Song usage history linked to plans

Phase 5 added optional one-to-one church-event links for worship plans and
rehearsals. When linked, event time/location is canonical and synchronized;
existing standalone Phase 4 schedules remain supported without duplication.

## Access rules

- Church Administrator: all implemented Phase 4 management capabilities.
- Worship Leader: song library/resources, worship plans, setlists,
  participation, and song assignments; no choir enrollment management.
- Choir Leader: roster, rehearsals, attendance, announcements, song assignments,
  and plan/song views; no song-library mutation.
- Choir Member: schedule and applicable announcements, song/resource views,
  participating plans, own attendance, and own song assignments only.
- Ministry Leader and Church Member: no automatic Phase 4 permissions.
- Anonymous users: redirected to login; authenticated unauthorized users receive
  HTTP 403.

Core records have no public hard-delete workflow. Setlist entries,
participations, and assignments can be removed as relationship-management
operations.

See [[../02-Architecture/Database-Design]],
[[../02-Architecture/Architecture-Decisions]], and
[[../04-Testing/Phase-4-Test-Results]].

The song title, artist, key, tempo, themes, category, plan associations, and
usage history remain ordinary structured domain data for future Phase 8 use.
No recommendation algorithm, score, endpoint, UI, or ML dependency exists.

Phase 6 extends this module with official Spotify track embeds, protected
resource previews and updates, ChordPro display, and rehearsal-song preparation.
See [[Song-Resources-Chord-Sheets]].

## Phase 7.3 milestone 5 interface

- Role-aware choir overview with actual enrollment, upcoming rehearsal,
  announcement, and own-assignment information
- Protected roster with name search, voice-part/status filters, summary cards,
  active Choir Leader names, pagination, and refined enrollment forms
- Upcoming, previous, and all-rehearsal views with search/status filters,
  selected-song summaries, optional church-event links, and responsive cards
- Rehearsal detail with authorized Spotify/resource access and attendance
  summaries for recorders; ordinary choir members receive only their own row
- Audience- and publication-aware announcement directory with management filters
- Refined song-assignment form limited to active worship-plan participants
- Worship Leader coordination access through existing schedule/roster
  permissions without automatically exposing choir announcements

No dedicated choir-management Figma frame was present in the exported file.
The UI therefore uses the audited CHORD desktop system and existing shared
components. The separate Inter/amber mobile practice design was not made global.
No notification service, new playback system, practice controls, automatic
chord generation, or recommendation behavior was added.

## Phase 7.3 milestone 6 worship-planning interface

- Permission-scoped upcoming, previous, and all-plan directory with search,
  preparation-status filters, actual summaries, and deterministic pagination
- Service detail patterned after the exported Approved Service Plan frame while
  retaining CHORD's real preparation statuses rather than approval/version state
- Existing church-event association shown only as a link when the event is also
  visible to the current account
- Ordered song setlist with key, tempo, category, themes, preparation notes,
  Spotify links, protected resources, and privacy-filtered assignments
- Existing up/down ordering and removal controls retained instead of adding
  unsupported drag-and-drop behavior
- Choir participation panel shows the full team only to roster-authorized users;
  Choir Members receive their own linked participation and assignments
- Refined create/edit plan, participant-selection, and add-song forms using the
  shared design system and existing transactional services

The Figma frame's generic non-song order items, approval identity, version
history, sharing/notification controls, worship-team position model, duration,
and conflict detection have no supporting domain and remain unimplemented. No
automatic song selection, recommendation UI, or Phase 8 behavior was added.
