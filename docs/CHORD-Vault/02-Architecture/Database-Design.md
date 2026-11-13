# Database Design

## Phase 2 account schema

- `accounts_user` — custom Django user with a many-to-many role relation.
- `accounts_profile` — one-to-one, small account profile; it intentionally does
  not duplicate future church-member records.
- `accounts_role` — stable code, display name, description, and Django
  permissions.
- `accounts_userrole` — through model with user, role, assigning user, and
  assignment time.
- `accounts_role_permissions` — responsibility permissions granted by a role.

`unique_user_role` prevents duplicate assignments. Deleting a user cascades its
assignments/profile; deleting an assigned role is protected. Deleting an
assigning administrator preserves the assignment but sets `assigned_by` null.

Migration `0002_alter_user_options_profile_role_userrole_user_roles_and_more`
preserves existing users, creates profiles for them, and seeds all six roles.

See [[Architecture-Decisions]] and [[../03-Modules/Authentication]].

## Phase 3 member schema

- `members_member` — UUID-addressed member identity, optional one-to-one user
  link, contact fields, membership status, dates, and timestamps.
- `members_memberauditevent` — application-controlled audit entries storing
  actor, action, timestamp, and changed field names without copied field values.

The user link is optional because not every church record needs login access.
One account can link to at most one member record. Future dates are rejected for
birth and join dates. Search indexes cover name and membership status. Audit
events protect member deletion, and no hard-delete workflow is exposed.

See [[../03-Modules/Member-Management]].

## QA verification

On 2026-11-07, live PostgreSQL introspection confirmed the unique user/role
constraint, one-to-one member/user constraint, unique member UUID, composite
name index, and membership-status index. Migration
`accounts.0003_alter_profile_phone_number` added consistent profile phone
validation without changing stored data.

## Phase 4 choir and worship schema

- `worship_choirenrollment` - one-to-one link to an existing member with voice
  part, participation status, joined date, and UUID.
- `worship_rehearsal` - scheduled rehearsal time, location, status, notes, and
  creator.
- `worship_rehearsalattendance` - one attendance state per rehearsal and choir
  enrollment.
- `worship_choirannouncement` - audience-scoped, publishable choir activity
  information with optional expiry.
- `worship_song` - UUID-addressed song metadata: title, artist, default key,
  tempo, category, bounded normalized theme list, and notes.
- `worship_songresource` - one licensed uploaded file or external URL with a
  required authorization reference. Files use protected storage.
- `worship_worshipplan` - service date/time, location, preparation status,
  notes, creator, setlist, and choir participation; Service Theme (nullable
  PROTECT FK to `traditions_theme`, required by the form for new plans),
  sermon title and scripture reference.
- `worship_plansong` - ordered setlist through model with planned key and notes.
- `worship_planchoirparticipation` - unique plan/enrollment participation.
- `worship_songassignment` - unique plan-song/enrollment responsibility with
  assignment metadata.

Constraints prevent duplicate attendance, setlist positions, songs within a
plan, plan participation, and song assignments. Check constraints validate song
tempo, positive setlist positions, and exactly one resource source. Composite
indexes support choir filtering, rehearsal schedules, song lookups, and plan
status/date queries. Migration `worship.0001_initial` is applied.

See [[../03-Modules/Choir-Worship-Management]] and
[[../04-Testing/Phase-4-Test-Results]].

## Phase 5 core integration schema

- `ministries_ministry` - UUID-addressed ministry, lifecycle status, creator,
  and timestamps.
- `ministries_ministrymembership` - one ministry/member assignment with
  leader/member role, status, joined date, notes, and assigning user.
- `events_event` - typed schedule, ministry, lifecycle status, visibility,
  registration controls, capacity, creator, and timestamps.
- `events_eventparticipant` - one event/member registration and attendance
  record with actor/timestamp metadata.
- `giving_fund` - named active/inactive contribution destination.
- `giving_contribution` - UUID-addressed identified or anonymous contribution,
  positive amount, date, method, reference, notes, and recording user.
- `giving_contributionauditevent` - immutable application audit metadata with
  changed field names only.
- `worship_rehearsal.event` and `worship_worshipplan.event` - nullable unique
  event links added by `worship.0002`.

Migrations `ministries.0001`, `events.0001`, `events.0002`, `giving.0001`, and
`worship.0002` are applied. Constraints prevent duplicate ministry membership,
duplicate event participation, non-positive contributions, and inconsistent
anonymous/member donors. Composite indexes support status/schedule, ministry/
schedule, participation state, attendance state, fund/date, and member/date
queries.

## Phase 6 resource schema changes

Migration `worship.0003_rehearsal_songs_song_spotify_track_id_and_more` adds:

- `worship_song.spotify_track_id` - optional validated 22-character normalized
  Spotify track ID.
- `worship_rehearsal_songs` - standard many-to-many table connecting rehearsal
  preparation to existing songs.
- `worship_songresource.updated_by_id` and `updated_at` - latest update metadata.
- ChordPro extensions in the existing protected resource file allowlist.

No ML table, feature vector, recommendation score, or playback data was added.
