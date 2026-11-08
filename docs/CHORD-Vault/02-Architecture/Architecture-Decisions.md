# Architecture Decisions

## 2026-11-06 — Role-permission design

- Use explicit `Role` and `UserRole` models instead of a single role field.
- Support multiple roles and retain assignment audit metadata.
- Attach Django `Permission` records to roles and resolve them with a small
  authentication backend so standard `has_perm` and permission mixins work.
- Do not treat Church Administrator as a superuser. Grant only account-related
  Phase 2 permissions; future modules own their permission mapping.
- Keep self-profile authorization object-specific in the view. Do not expose an
  arbitrary profile identifier.
- Keep choir participation separate from RBAC because participation is domain
  membership, not system authorization.
- Use built-in Django authentication/password/session functionality instead of
  an external authentication framework.

This is the simplest design that supports responsibility-based permissions,
multiple roles, auditable assignments, and incremental future modules.

See [[Database-Design]], [[../01-Project/User-Roles]], and
[[../03-Modules/Authentication]].

## 2026-11-06 — Member privacy and auditing

- Use non-sequential UUIDs in member URLs.
- Keep member records separate from authentication profiles and link them
  optionally one-to-one.
- Separate directory access, sensitive-field access, and management permission.
- Allow account owners to view only their linked record through `/members/me/`.
- Store field names, not sensitive old/new values, in audit events.
- Use membership status rather than a public hard-delete workflow.
- Search email only for users with sensitive-data permission.

See [[../03-Modules/Member-Management]] and [[Database-Design]].

## 2026-11-07 — QA security hardening

- Treat role mappings in code as authoritative and replace stale Church
  Administrator permissions during post-migration synchronization.
- Require custom management permission plus the matching Django add/change
  permission for account and member mutations.
- Share one model-level phone validator across profiles and member records.
- Keep development security flags false locally, but expose secure cookies,
  HTTPS redirect, and HSTS through environment variables for production.
- Preserve list performance with role prefetching and avoid unused joins.

See [[../04-Testing/Phases-1-3-QA-Audit]].
