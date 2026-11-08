# Development Log

## 2026-11-06 — pre-development setup

- Inspected the existing Django 6.1 bootstrap and preserved its files.
- Found Python 3.14.7; Python 3.12 is not installed.
- Verified PostgreSQL 17.11 service and local port 5432.
- Confirmed PostgreSQL administration requires a password, so no database or
  role was changed.
- Created `.venv`; installed Django 5.2.19 LTS and requested tools.
- Reconfigured Django for environment-driven PostgreSQL access and Manila time.
- Added `accounts.User` before any PostgreSQL migrations and generated its
  initial migration.
- Added tests, Ruff configuration, Git repository files, and this vault.
- Passed two settings-only tests, Django checks, dependency validation, Ruff
  lint, Ruff formatting, and migration-drift validation.
- Confirmed migrations, the full three-test suite, and server startup are
  blocked specifically by the intentionally unset PostgreSQL password.

## 2026-11-06 — PostgreSQL completion verification

- Confirmed `.env` contains credentials without displaying them.
- Connected to `chord_db` as `chord_user` on PostgreSQL 17.11.
- Verified Django resolves the custom model as `accounts.User` before migration.
- Applied all initial migrations and verified 10 tables, including
  `accounts_user`, `django_migrations`, and `django_session`.
- Passed dependency, migration-drift, Django system, Ruff lint, and Ruff format
  checks.
- Started the development server and received HTTP 200 at `127.0.0.1:8000`.
- The full test suite found three tests but could not create `test_chord_db`
  because `chord_user` lacks `CREATEDB`; documented the minimal pgAdmin fix.
- Granted `chord_user` the local `CREATEDB` capability through pgAdmin.
- Reran all three tests successfully against an isolated PostgreSQL test
  database and confirmed Django removed `test_chord_db` afterward.
- Repeated system, migration-drift, dependency, Ruff lint, and Ruff format
  checks; all passed. The environment is ready for master development.

See [[Known-Issues]] and [[../04-Testing/Environment-Verification]].

## 2026-11-06 — Phase 3 member management

- **Phase:** 3
- **Task:** Privacy-aware member record management.
- **Files:** Created `apps/members/`, templates, migration `0001`, and Phase 3
  tests; updated permission synchronization, navigation, URLs, and vault notes.
- **Implementation:** Added member records, optional account linking, status,
  contact/date validation, search/filtering, self-record access, scoped
  sensitive fields, account management workflows, and audit events.
- **Security:** UUID URLs, server-side object access, separate sensitive-data
  permission, email-search restriction, no delete permission/workflow, and audit
  logs containing field names rather than confidential values.
- **Tests:** 32 combined tests passed. System, migration-drift, dependency, Ruff
  lint/format, schema/permission, and server route checks passed.
- **Refactoring:** Smoke testing found and fixed anonymous 403 behavior while
  preserving authenticated-denial 403 responses.
- **Problems:** The first smoke-test request returned 403 instead of a login
  redirect; fixed and covered by regression test.
- **Next:** Stop at the phase boundary. Ministry management is recommended next
  only after authorization.

See [[../03-Modules/Member-Management]], [[Refactoring-Log]], and
[[../04-Testing/Phase-3-Test-Results]].

## 2026-11-06 — Phase 2 authentication and RBAC

- **Phase:** 2
- **Task:** Authentication, profiles, account management, and multi-role RBAC.
- **Files:** Updated `config/settings.py`, `config/urls.py`, the accounts app,
  README, templates, migration `0002`, tests, and this vault.
- **Implementation:** Added six seeded roles, `Role`, `UserRole`, `Profile`, a
  role-permission backend, secure login/POST logout, password changes,
  self-profile editing, and permission-protected account administration.
- **Security:** Church Administrator is not a superuser and receives only Phase
  2 account permissions. Inactive users receive no role permissions. Users
  cannot deactivate themselves or change their own roles through the UI.
- **Tests:** 17 Django tests passed. Django checks, migration drift, dependency
  checks, Ruff lint, Ruff formatting, and server login/redirect smoke checks
  passed.
- **Refactoring:** Corrected form save ordering so every role assignment created
  through account management retains its `assigned_by` audit record.
- **Problems:** One audit test initially failed and drove the save-order fix.
- **Next:** Stop at the phase boundary. Begin member management only after user
  authorization.

See [[../03-Modules/Authentication]], [[Refactoring-Log]], and
[[../04-Testing/Phase-2-Test-Results]].

## 2026-11-06 — Initial administrator bootstrap

- **Phase:** 2 follow-up
- **Task:** Bootstrap and verify the first administrator.
- **Implementation:** The user created a local Django superuser and assigned the
  Church Administrator role through Django admin.
- **Verification:** Confirmed one active Church Administrator assignment, one
  superuser, and a clean Django system check without displaying account details.
- **Next:** Optionally create a separate non-superuser Church Administrator for
  routine use; keep the superuser for framework administration and recovery.

## 2026-11-07 — Comprehensive Phases 1–3 QA audit

- **Phase:** Pre-Phase 4 quality gate
- **Task:** Verify implementation, database architecture, security, features,
  tests, and documentation against the actual repository.
- **Files:** Reviewed all source, templates, migrations, settings, root files,
  and vault notes. Updated permissions, validators, settings, templates, tests,
  README, migration `accounts.0003`, and audit documentation.
- **Refactoring:** Tightened action permissions, made role synchronization
  authoritative, shared phone validation, removed an unused join, and added
  reusable pagination plus secure production environment switches.
- **Security:** Added CSRF/HTTP-method regressions, mutation-denial tests, stale
  permission removal, production `check --deploy` simulation, and secret-ignore
  verification.
- **Database:** PostgreSQL introspection confirmed required tables, unique
  constraints, one-to-one linkage, UUID uniqueness, and member indexes.
- **Tests:** Expanded from 32 to 44; all passed. Django checks, migration drift,
  dependency validation, Ruff lint/format, and live server smoke checks passed.
- **Issues:** No critical issue. Git has no baseline commit, role removals lack a
  durable application audit event, and login rate limiting remains a production
  hardening item.
- **Next:** Review and create a Git baseline commit, then begin Phase 4 only when
  explicitly authorized.

See [[../04-Testing/Phases-1-3-QA-Audit]], [[Known-Issues]], and
[[Refactoring-Log]].
