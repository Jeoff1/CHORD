# Phase 7 Test Results

Verified: **2026-11-10**
Current scope: **Phase 7.3 milestone 4 - attendance and giving**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| Attendance, giving, and shell tests | Pass - 35 tests in 14.735 seconds |
| Milestone regression set | Pass - 64 tests in 25.555 seconds |
| Full Django suite | Pass - 137 tests in 63.357 seconds |
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

No models or migrations were added. Browser verification rendered the exported
Attendance and Giving reference crops; authenticated application screenshot
comparison remains a manual follow-up. Payments, exports, reconciliation,
notifications, broader reporting, and Phase 8 recommendation behavior remain
outside this milestone.
