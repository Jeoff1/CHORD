# Phase 7 Test Results

Verified: **2026-11-10**
Current scope: **Phase 7.3 milestone 3 - ministries and church events**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| Ministry and event tests | Pass - 23 tests in 9.029 seconds |
| Milestone regression set | Pass - 58 tests in 22.896 seconds |
| Full Django suite | Pass - 129 tests in 61.596 seconds |
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

No models or migrations were added. Browser verification rendered the exported
SVG reference board and relevant crops; authenticated application screenshot
comparison remains a manual follow-up. Booking, notification, reporting, and
Phase 8 recommendation behavior remain outside this milestone.
