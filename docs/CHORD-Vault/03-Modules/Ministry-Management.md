# Ministry Management

Status: **Completed - Phase 5 (2026-11-09)**

## Implemented

- Active/inactive ministries with UUID application URLs
- Reuse of existing `Member` records for ministry participation
- One membership per ministry/member with leader/member role, status, join
  date, notes, assigning user, and timestamps
- Searchable ministry directory with active-member counts
- Church Administrator ministry creation and global management
- Ministry Leader updates and roster management only for an assigned ministry
- Protection against active assignments for inactive church members

## Authorization boundary

The Ministry Leader system role grants capability, while an active leader
`MinistryMembership` grants the object scope. Both are required. Ministry
Leaders cannot assign other leaders; that responsibility remains with Church
Administrators. General directory viewers do not receive the management roster.

See [[Events-Attendance]], [[../02-Architecture/Database-Design]], and
[[../04-Testing/Phase-5-Test-Results]].
