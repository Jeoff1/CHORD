# Events and Attendance

Status: **Core completed in Phase 5; Phase 7.3 UI refined (2026-11-10)**

## Implemented

- Church-wide calendar with search and type, ministry, and timing filters
- Worship service, rehearsal, ministry, fellowship, outreach, training, and
  general event types
- Draft, published, completed, and cancelled lifecycle states
- Church-wide, ministry-member, and ministry-leader visibility
- Optional registration deadline and capacity
- Transactional registration with automatic waitlisting and first-in
  waitlist promotion after cancellation
- Manager-added participants and bulk attendance states
- Actor/timestamp metadata for registration and attendance
- Assigned Ministry Leader object management and global Church Administrator
  management

## Phase 7.3 interface

- Upcoming, past, and all-event segments with truthful counts
- Search, event-type, and ministry filtering with filter-preserving pagination
- Responsive event cards showing lifecycle, audience, ministry, location,
  registration count, capacity progress, and waitlist count
- Event detail presentation with schedule, linked worship/rehearsal records,
  registration state, cancellation, participant management, and attendance
- Registration-open messaging that respects publication, start time, and
  registration deadline while retaining service-layer validation
- Permission-aware create/edit, participant, and attendance forms with clear
  validation and empty states
- Deterministic pagination and selected related data for efficient rendering
- Permission-scoped attendance overview and history using existing event
  participant records
- Manageable-event and date-range filters with real participant, present,
  absent, and not-recorded summaries
- Separate role-aware Attendance navigation for authorized administrators and
  ministry leaders
- Responsive attendance history and per-event forms with semantic status pills

## Phase 4 integration

`WorshipPlan.event` and `Rehearsal.event` are optional one-to-one links. When
linked, the event is the canonical time/location and event edits synchronize
those fields. Existing unlinked Phase 4 records remain valid and unchanged.
Linked event types cannot be changed to an incompatible type through validated
workflows.

No recurring-event engine or notification service was added; neither is needed
for the verified Phase 5 core workflow.

The Figma week grid, church service requests, rooms/resources, bookings,
payments, full active-member attendance roster, first-time guests, roster
export, and bulk attendance shortcuts remain unimplemented and are not shown as
functional controls.

See [[Ministry-Management]], [[Choir-Worship-Management]], and
[[../04-Testing/Phase-5-Test-Results]].
