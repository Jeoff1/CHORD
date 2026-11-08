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

## 2026-11-08 - Phase 4 choir and worship domain

- Use one cohesive `worship` app because choir preparation, song resources,
  setlists, and service plans share permissions and relationships.
- Keep `ChoirEnrollment` separate from the Choir Member role: enrollment is
  domain participation, while roles authorize application capabilities.
- Reuse `members.Member` for choir identity rather than duplicating personal or
  contact data.
- Grant authoritative, responsibility-scoped permissions to Church
  Administrator, Worship Leader, Choir Leader, and Choir Member roles.
- Filter worship plans, song assignments, song usage, and rehearsal attendance
  at the queryset level for participant accounts.
- Store normalized worship themes as a bounded JSON string list. This supports
  future recommendation inputs without implementing an ML engine or premature
  taxonomy tables.
- Store licensed uploads outside public media, require an authorization
  reference, validate extension and size, and stream files only through a
  permission-protected view.
- Use explicit through models for ordered setlists, choir participation, and
  song assignments. Database constraints protect ordering and uniqueness.
- Keep service scheduling on `WorshipPlan` because no event module exists.
  Introduce an event foreign key only in the later event phase.
- Lock parent/setlist rows during synchronization and reordering to prevent
  concurrent edits from producing stale positions.

See [[../03-Modules/Choir-Worship-Management]], [[Database-Design]], and
[[../04-Testing/Phase-4-Test-Results]].
