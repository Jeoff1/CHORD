# Phase 2 Test Results

Date: 2026-11-06  
Phase: 2 — Authentication and RBAC  
Result: **Pass**

## Automated results

- `python manage.py test --verbosity 2`: 17 tests passed.
- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes detected.
- `python -m pip check`: no broken requirements.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed.

Coverage includes PostgreSQL access, seeded roles, multiple-role uniqueness,
profiles, scoped permissions, inactive users, non-superuser boundaries, login,
POST logout, password changes, self-profile isolation, 403 authorization,
account creation/deactivation, role-assignment audit data, and self-lockout
protection.

## Server smoke test

- `/login/` returned HTTP 200 and contained a CSRF token.
- Unauthenticated `/` returned HTTP 302 to login.
- The test server was stopped after verification.

## Issue found and resolved

The initial run passed 15 of 16 tests. The role-assignment audit test found a
form save-order defect. After refactoring and adding deactivation coverage, the
full 17-test suite passed.

See [[../03-Modules/Authentication]] and
[[../03-Development/Refactoring-Log]].
