# Phase 5 Test Results

Verified: **2026-11-09**

## Automated results

| Check | Result |
| --- | --- |
| `manage.py check` | Pass - no issues |
| `makemigrations --check --dry-run` | Pass - no model drift |
| `manage.py migrate` | Pass - five Phase 5 migrations applied |
| Full Django suite | Pass - 94 tests in 42.761 seconds |
| PostgreSQL test database cleanup | Pass |
| `ruff check .` | Pass |
| `ruff format --check .` | Pass - 110 files formatted |
| Development server | Pass - HTTP response verified locally |

## Added coverage

Twenty-five Phase 5 tests cover ministry validation and object authority; event
audience filtering; unauthorized access; leader scoping; registration,
capacity, waitlisting, cancellation promotion, and worship schedule sync;
contribution validation; confidential management; member-only self-history;
anonymous giving; and audit creation. The existing 69 Phase 1-4 tests remained
green.

## Security review

- Mutations require custom responsibility permissions and matching Django
  action permissions.
- Ministry and event management also require active leader membership for the
  target object.
- Event detail queries enforce audience visibility server-side.
- Attendance submissions accept participants only from the target event.
- Contribution administration is not granted to member-facing roles.
- Personal giving queries join through the authenticated user's member record.
- `.env` remains ignored and no credential value was read into documentation.

No critical or high-severity Phase 5 issue remains. See
[[../03-Development/Known-Issues]].
