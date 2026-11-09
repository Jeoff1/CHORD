# Events and Attendance

Status: **Completed - Phase 5 (2026-11-09)**

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

## Phase 4 integration

`WorshipPlan.event` and `Rehearsal.event` are optional one-to-one links. When
linked, the event is the canonical time/location and event edits synchronize
those fields. Existing unlinked Phase 4 records remain valid and unchanged.
Linked event types cannot be changed to an incompatible type through validated
workflows.

No recurring-event engine or notification service was added; neither is needed
for the verified Phase 5 core workflow.

See [[Ministry-Management]], [[Choir-Worship-Management]], and
[[../04-Testing/Phase-5-Test-Results]].
