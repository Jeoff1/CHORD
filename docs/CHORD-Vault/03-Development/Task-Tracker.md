# Task Tracker

## Completed

- [x] Audit Windows, Python, Git, PostgreSQL, and existing CHORD files
- [x] Create `.venv` and install pinned setup dependencies
- [x] Configure environment-driven Django settings for PostgreSQL
- [x] Create `accounts.User` and its initial migration
- [x] Initialize Git and create ignore rules
- [x] Create the Obsidian vault and setup documentation
- [x] Create and connect to `chord_db` as `chord_user`
- [x] Add the application password to untracked `.env`
- [x] Apply all initial migrations and verify 10 database tables
- [x] Pass Django checks, migration drift, Ruff lint, and Ruff format checks
- [x] Start the development server and receive HTTP 200
- [x] Grant local `CREATEDB` for isolated Django test databases
- [x] Pass the full three-test suite and verify test-database cleanup

## Remaining setup action

- None

## Future master-development work

- [x] Phase 2 — authentication and multi-role RBAC
- [x] Phase 3 — member management
- [ ] Later church-management modules
- [ ] Worship planning, song library, and recommendations
- [ ] Integrations, reporting, and deployment preparation

See [[Known-Issues]] and [[../04-Testing/Environment-Verification]].

## Phase 2 completed

- [x] Login and POST-only logout
- [x] Password change with authenticated-session preservation
- [x] Automatic self-service account profiles
- [x] Six seeded responsibility-based roles
- [x] Multiple roles per user with unique database constraint
- [x] Audited role assignment (`assigned_by`, `assigned_at`)
- [x] Permission backend and server-side authorization enforcement
- [x] Scoped Church Administrator account permissions
- [x] Account creation, activation/deactivation, and role assignment
- [x] Self-deactivation and self-role-removal protection
- [x] Phase 2 migration, tests, lint, formatting, and server verification
- [x] Bootstrap the first active Church Administrator account

## Phase 3 completed

- [x] Member record model and optional account linking
- [x] Membership status and date validation
- [x] Privacy-aware member directory with search and status filtering
- [x] Self-only linked member-record access
- [x] Separate directory, sensitive-data, and management permissions
- [x] Create and update workflows without public hard deletion
- [x] Audit events that store changed field names without sensitive values
- [x] Django admin integration and auditing
- [x] PostgreSQL migration and scoped Church Administrator permission sync
- [x] 32 combined tests, lint, format, migration, and server verification

## Phases 1–3 QA audit completed

- [x] Review source, templates, migrations, settings, and complete vault
- [x] Verify PostgreSQL tables, relationships, constraints, and indexes
- [x] Tighten create/update permissions to exact Django actions
- [x] Remove stale administrator permissions during role synchronization
- [x] Add shared phone validation to account profiles
- [x] Remove an unused member-directory join
- [x] Add working pagination controls to account and member lists
- [x] Add environment-driven production security switches
- [x] Expand critical security, validation, pagination, role, and N+1 tests
- [x] Apply migration `accounts.0003_alter_profile_phone_number`
- [x] Pass 44 tests and all final automated checks
- [x] Verify live server redirects and secure deployment-settings simulation
