# Phase 7 Test Results

Verified: **2026-11-10**
Current scope: **Phase 7.3 milestone 6 - worship planning**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| Worship planning and resource integration | Pass - 16 tests in 20.322 seconds |
| Worship, choir, resource, dashboard, and shell regressions | Pass - 59 tests in 43.554 seconds |
| Full Django suite | Pass - 149 tests in 85.690 seconds |
| PostgreSQL test database cleanup | Pass |
| `ruff check .` | Pass |
| `ruff format --check .` | Pass - 125 files compliant |

## Milestone coverage

- Administrator dashboard renders real cross-module data and working actions.
- Member dashboard excludes events outside the member's visibility scope.
- Choir assignments and active ministry memberships render from linked records.
- Administrator financial summary and actions do not appear to regular members.
- Accounts without a linked member record receive an accurate empty state.
- Existing shell permission and unimplemented-feature assertions remain green.
- Directory ministry/status/segment filtering and filter-preserving pagination.
- Prefetched ministry and choir affiliations render without template lookups.
- Limited directory viewers receive no email, phone, or contact column.
- Profile and edit screens render supported affiliations and attendance.
- Attendance excludes events outside the viewer's visibility scope.
- Administrator ministry status filtering and active-leader presentation.
- General directory viewers can see leaders but cannot access management rosters.
- Ministry activity panels include only visible upcoming events.
- Event upcoming/past segmentation and capacity/waitlist counts.
- Member screens omit event management actions.
- Registration views show waitlist state and cancellation promotes the oldest
  waiting participant through the existing transactional service.
- Attendance overview aggregates existing participant statuses and respects
  selected event/date filters.
- Regular members cannot access attendance overview or direct recording routes;
  ministry leaders cannot record attendance for another ministry's event.
- Giving date/fund filters drive actual authorized totals and ledger rows.
- Fund directory totals use real contributions.
- Member giving history excludes every other donor and internal reference.
- Members cannot access fund administration or contribution creation routes.
- Choir overview uses actual enrollment/rehearsal/announcement/assignment data.
- Choir Members see only their own song assignments and rehearsal attendance.
- Choir roster filtering preserves truthful unfiltered participation summaries.
- Upcoming and previous rehearsal segments use deterministic date ordering.
- Choir Leaders can render and submit enrollment, rehearsal, attendance,
  announcement, and assignment workflows under existing permissions.
- Worship Leaders can coordinate schedules and roster participation without
  receiving choir-announcement access they do not possess.
- Rehearsal and assignment screens preserve Spotify and protected-resource access.
- Plan directories enforce scoped upcoming/previous/status filtering and counts.
- Linked worship events supply canonical date, time, and location through the
  existing validated form.
- Choir Members receive no plan-management controls or other members' assignments.
- Unauthorized ordinary accounts receive HTTP 403 on direct plan access.
- Plan forms and add-song forms render the shared design controls.
- Move and remove endpoints preserve contiguous transactional setlist ordering.
- Plan details retain Spotify links and protected resources from Phase 6.

No models or migrations were added. The local Approved Service Plan frame was
rendered and inspected; authenticated application screenshot comparison remains
a manual follow-up. Generic service items, approval/version history, team
sharing, conflicts, notifications, automatic song selection, and Phase 8
recommendation behavior remain outside this milestone.

## Phase 7A ticket 12: demo churches (2026-11-13)

`apps/traditions/tests_seed.py` (11 tests) covers `seed_tradition` for all
three presets: a complete church per Tradition; no duplicates when re-run, or
when switching Traditions and back (users, role assignments, members, songs,
song-theme links, plans, setlist items, records); metadata-only songbooks hold
no resources or notes; no usable passwords or non-`example.com` emails; and the
real-data guard (refuses a renamed Church Profile or non-demo members unless
`--force`). Full suite: 275 tests passed.

## Phase 7A ticket 13: Phase 8 inputs and close-out (2026-11-15)

`apps/traditions/tests_slot_context.py` (3 tests) covers
`services.slot_context()`: one call returns the plan's Service Theme, derived
Season (Lent for a March 2027 Mass), allowed Songbooks and target Song Slot;
Season is None outside every Season; a Song Slot from another Service Template
raises `ValueError`. Full suite: 278 tests passed in 138.166 seconds;
`manage.py check`, `makemigrations --check`, `ruff check .` and
`ruff format --check .` (201 files) all pass. **Phase 7A is complete.**
