# Phases 1–3 QA Audit

Date: 2026-11-07  
Scope: Development foundation, authentication/RBAC, and member management  
Result: **READY FOR PHASE 4**

## Verified implementation

- Django 5.2.19 uses PostgreSQL 17.11 as `chord_user` on `chord_db`.
- Environment credentials are populated locally; `.env` is ignored and not
  tracked by Git.
- The custom `accounts.User`, six roles, multi-role through model, profiles,
  permission backend, authentication routes, and account workflows exist.
- Member records, optional account links, UUID routes, privacy boundaries,
  validation, search/filtering, pagination, and audit events exist.
- Required PostgreSQL tables and all migrations are applied.
- Live introspection confirmed role uniqueness, one-to-one account/member
  linkage, UUID uniqueness, and member name/status indexes.
- Account lists prefetch roles; the member list no longer performs an unused
  user join. A regression test asserts two-query account/role loading.

## Security verification

- Anonymous protected requests redirect to login; authenticated denied requests
  receive HTTP 403.
- Logout is POST-only and profile mutation rejects missing CSRF tokens.
- Account and member mutations require exact server-side permissions.
- Inactive users receive no role permissions; administrators cannot remove
  their own role or deactivate themselves through the account UI.
- Directory-only viewers cannot see sensitive member fields or search by email.
- Member audit events store changed field names, not sensitive values.
- Phone and date validation reject malformed/future values.
- Secure cookies, HTTPS redirect, and HSTS are environment-configurable. A
  simulated production environment passed `check --deploy` with no warnings.

## Refactoring performed

- Exact create/update permission mixins for accounts and members.
- Authoritative Church Administrator permission synchronization.
- Shared profile/member phone validator and migration `accounts.0003`.
- Removed unused member query join.
- Added reusable, filter-preserving pagination.
- Added production security environment switches.
- Added 12 meaningful regression tests.

## Actual final commands and results

- `python manage.py test --verbosity 1`: **44 tests passed**.
- `python manage.py check`: **no issues**.
- `python manage.py makemigrations --check --dry-run`: **no changes detected**.
- `python -m pip check`: **no broken requirements**.
- `python -m ruff check .`: **passed**.
- `python -m ruff format --check .`: **56 files already formatted**.
- `python manage.py check --deploy` with simulated secure production values:
  **no issues**.
- Live server: `/login/` returned 200; `/`, `/members/`, and `/admin/` returned
  the expected anonymous redirects. The server was stopped afterward.

## Coverage gaps and remaining risks

- **Medium:** All repository source remains untracked because no initial Git
  commit exists. Create a reviewed baseline commit before Phase 4.
- **Medium:** Removing a role assignment deletes the through row; there is no
  durable application audit event specifically for role removal. Django admin
  logging and current assignment metadata remain available.
- **Medium (production):** No login rate limiting is implemented. Add a reviewed
  solution before public deployment; it is not required for local Phase 4 work.
- **Low:** Bootstrap CSS is CDN-hosted without an offline asset strategy.
- **Low:** The unused original `venv/` and `db.sqlite3` remain ignored on disk.
- **Design decision:** Profile and member contact fields remain separate and are
  not automatically synchronized.

No critical issue remains. Phase 4 may begin after the user authorizes it.

Historical note: the baseline-commit issue recorded above was resolved by commit
`6686960` before Phase 4 completion. See [[Phase-4-Test-Results]] for the current
verification state.

See [[../03-Development/Known-Issues]], [[../03-Development/Task-Tracker]],
[[../02-Architecture/Database-Design]], and [[../03-Development/Refactoring-Log]].
