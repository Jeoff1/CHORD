# Ministry Management

Status: **Core completed in Phase 5; Phase 7.3 UI refined (2026-11-10)**

## Implemented

- Active/inactive ministries with UUID application URLs
- Reuse of existing `Member` records for ministry participation
- One membership per ministry/member with leader/member role, status, join
  date, notes, assigning user, and timestamps
- Searchable ministry directory with active-member counts
- Church Administrator ministry creation and global management
- Ministry Leader updates and roster management only for an assigned ministry
- Protection against active assignments for inactive church members

## Phase 7.3 interface

- Searchable team-card directory with administrator-only status filtering
- Active-member counts and active leader presentation without exposing notes
  or private contact fields
- Responsive detail composition with purpose, status, leaders, and only the
  upcoming events visible to the current account
- Object-scoped roster management, enrollment, edit actions, validation states,
  and consistent shared form controls
- Prefetched active leaders and selected roster relations to avoid template
  N+1 queries

## Authorization boundary

The Ministry Leader system role grants capability, while an active leader
`MinistryMembership` grants the object scope. Both are required. Ministry
Leaders cannot assign other leaders; that responsibility remains with Church
Administrators. General directory viewers do not receive the management roster.

Volunteer shifts, assignments, availability requests, coverage, and conflict
detection shown in the design reference remain unimplemented backend domains.

See [[Events-Attendance]], [[../02-Architecture/Database-Design]], and
[[../04-Testing/Phase-5-Test-Results]].
