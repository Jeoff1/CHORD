# Phase 7 Test Results

Verified: **2026-11-10**
Current scope: **Phase 7.3 milestone 5 - choir management**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| Choir, worship-resource, dashboard, and shell regressions | Pass - 53 tests in 31.327 seconds |
| Protected rehearsal resource recheck | Pass - 2 tests in 1.332 seconds |
| Full Django suite | Pass - 143 tests in 71.098 seconds |
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

No models or migrations were added. Browser verification rendered the exported
file for earlier screen groups, but it contains no dedicated choir-management
frame. Authenticated application screenshot comparison remains a manual
follow-up. Notifications, custom playback, advanced practice controls,
automatic chord generation, and Phase 8 recommendation behavior remain outside
this milestone.
