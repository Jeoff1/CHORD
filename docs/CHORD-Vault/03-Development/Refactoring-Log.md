# Refactoring Log

## 2026-11-06 — Phase 2 account form audit preservation

- **Problem:** Django's default model-form many-to-many save created role
  assignments before the custom audit code, leaving `assigned_by` empty.
- **Change:** Save the user instance without automatic many-to-many handling,
  then reconcile role assignments explicitly inside the existing transaction.
- **Result:** The audit regression test passes and all assignments created from
  the account UI record their assigning administrator.
- **Scope:** `apps/accounts/forms.py`; no unrelated modules changed.

See [[Development-Log]] and [[../04-Testing/Phase-2-Test-Results]].

## 2026-11-06 — Anonymous permission handling

- **Problem:** Server smoke testing found anonymous `/members/` access returned
  HTTP 403 because the permission mixin raised for every denial.
- **Change:** Added a shared authenticated-permission mixin that redirects
  anonymous users to login while retaining HTTP 403 for authenticated users who
  lack permission.
- **Result:** `/members/` now returns HTTP 302 to `/login/?next=/members/`; a
  regression test protects this behavior.
- **Scope:** Shared accounts mixin and permission-protected account/member views.

## 2026-11-07 — Phases 1–3 QA refactoring

- Split account create/update permission requirements so each action checks its
  exact Django model permission.
- Hardened member mutations with add/change and sensitive-data permissions.
- Changed role synchronization from additive updates to an authoritative set,
  preventing stale administrator grants.
- Reused one phone validator across profiles and member records.
- Removed an unused `select_related("user")` from the member directory.
- Added a shared pagination partial and preserved member filters between pages.
- Added environment-driven secure-cookie, HTTPS, and HSTS settings.
- Expanded regression coverage from 32 to 44 tests, including a two-query
  account/role prefetch assertion.

No unrelated application module was introduced.

## 2026-11-08 - Phase 4 review and refactoring

- Reused `members.Member` instead of introducing duplicate choir identity data.
- Kept choir participation separate from RBAC roles.
- Centralized plan participant, setlist, assignment, and attendance mutations in
  transactional services.
- Added row locking around synchronization and ordering so concurrent edits do
  not create stale setlist positions.
- Reused the shared pagination partial and generalized its preserved query
  string support for additional Phase 4 filters.
- Prevented member accounts from seeing other singers' attendance, assignments,
  or non-participating worship-plan usage history.
- Deferred object lookup until after permission checks on resource/setlist
  creation endpoints, reducing identifier probing.
- Moved licensed uploads from public media to protected storage and retained a
  single authenticated download path.
- Disabled changing the member identity of an existing choir enrollment to
  preserve rehearsal and assignment history.

See [[../04-Testing/Phase-4-Test-Results]].
