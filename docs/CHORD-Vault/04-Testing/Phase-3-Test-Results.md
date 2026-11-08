# Phase 3 Test Results

Date: 2026-11-06  
Phase: 3 — Member Management  
Result: **Pass**

## Automated results

- `python manage.py test --verbosity 1`: 32 tests passed.
- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes detected.
- `python -m pip check`: no broken requirements.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: 53 files formatted.

Member tests cover model defaults, one-to-one account integrity, future-date
validation, scoped administrator permissions, directory denial, anonymous login
redirect, search/filtering, sensitive email search, self-record access,
cross-record denial, sensitive-field hiding, missing links, audit creation, and
status-change auditing. All Phase 1–2 regression tests also pass.

## Live verification

- Migration `members.0001_initial` applied successfully.
- `members_member` and `members_memberauditevent` exist in PostgreSQL.
- Church Administrator has seven scoped member permissions and no delete member
  permission.
- `/login/` returned HTTP 200.
- Anonymous `/members/` returned HTTP 302 to `/login/?next=/members/`.
- The development server was stopped after verification.

## Issue found and resolved

Initial smoke testing found anonymous directory access returned 403. A shared
permission mixin now distinguishes unauthenticated redirects from authenticated
authorization failures, and a regression test verifies it.

See [[../03-Modules/Member-Management]] and
[[../03-Development/Refactoring-Log]].
