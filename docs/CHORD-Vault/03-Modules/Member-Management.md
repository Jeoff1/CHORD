# Member Management

Status: **Backend completed in Phase 3; UI refined in Phase 7.3 Milestone 2
(2026-11-10)**

## Implemented

- Member names, contact information, address, birth/join dates, and status
- Visitor, Regular Attendee, Member, and Inactive statuses
- Optional one-to-one link to a CHORD account
- Directory search by name and permitted email/phone, plus active-ministry and
  status filtering
- Derived All, Active, New in 30 days, and Inactive directory segments
- Pagination that preserves active search, segment, ministry, and status filters
- Prefetched active ministry and choir affiliations in the directory
- UUID-based detail/edit URLs
- Linked users' self-record view
- Create and update workflows for authorized administrators
- Field-name-only audit events for creation, updates, and status changes
- Read-only audit administration in Django admin
- Responsive Figma-aligned directory, detail, create, and edit templates
- Member profile affiliation summaries and permission/visibility-scoped recent
  attendance

## Access rules

- Church Administrator: directory, sensitive fields, creation, and updates;
  mutations require both the custom management permission and the matching
  Django add/change permission.
- Linked account owner: only their own record, including their own sensitive
  fields.
- Directory-only permission: non-sensitive record details only.
- Other authenticated users: no directory or other member record access.
- Anonymous users: redirected to login.

No public hard-delete route exists. Phase 7.3 displays existing ministry, choir,
and attendance relationships but does not move their management into the member
domain. Giving is never queried or shown on member profiles. Family/household,
contact verification, import/export, availability, and generic activity history
remain unimplemented.

See [[../02-Architecture/Database-Design]],
[[../02-Architecture/Architecture-Decisions]], and
[[../04-Testing/Phase-3-Test-Results]], and
[[../04-Testing/Phase-7-Test-Results]].
