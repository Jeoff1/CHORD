# Member Management

Status: **Completed — Phase 3 (2026-11-06)**

## Implemented

- Member names, contact information, address, birth/join dates, and status
- Visitor, Regular Attendee, Member, and Inactive statuses
- Optional one-to-one link to a CHORD account
- Directory search by name and permitted email, plus status filtering
- Pagination that preserves active search and status filters
- UUID-based detail/edit URLs
- Linked users' self-record view
- Create and update workflows for authorized administrators
- Field-name-only audit events for creation, updates, and status changes
- Read-only audit administration in Django admin

## Access rules

- Church Administrator: directory, sensitive fields, creation, and updates;
  mutations require both the custom management permission and the matching
  Django add/change permission.
- Linked account owner: only their own record, including their own sensitive
  fields.
- Directory-only permission: non-sensitive record details only.
- Other authenticated users: no directory or other member record access.
- Anonymous users: redirected to login.

No public hard-delete route exists. Ministry membership, choir affiliation,
attendance, giving, and family/household modeling are not part of Phase 3.

See [[../02-Architecture/Database-Design]],
[[../02-Architecture/Architecture-Decisions]], and
[[../04-Testing/Phase-3-Test-Results]].
