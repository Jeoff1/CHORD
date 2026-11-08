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

No church-wide event module existed at implementation time. The plan owns the
service schedule and exposes the correct future integration boundary; Phase 4
does not create duplicate or speculative event records.

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
