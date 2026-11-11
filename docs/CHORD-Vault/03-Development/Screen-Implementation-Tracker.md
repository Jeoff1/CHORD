# Screen Implementation Tracker

**Phase 7.3 milestone 6 result:** Dashboard, member-management, ministry,
church-event, attendance, giving, choir-management, and worship-planning screen
groups complete. The shared shell remains the Phase 7.2 foundation; other Figma
screens remain separate milestones.

Every existing authenticated Django screen now inherits the role-aware shell,
header, responsive drawer, design tokens, and shared Bootstrap refinements from
`base.html`. This does not mean the 19 Figma screens are individually complete.

| Figma screen | Current implementation status |
| --- | --- |
| Community operations · Admin overview | **Implemented in 7.3 milestone 1:** permission-scoped metrics, quick actions, upcoming events, recent members, worship preparation, and confidential monthly giving summary |
| Community operations · Member directory | **Implemented in 7.3 milestone 2:** segmented counts, privacy-aware search, ministry/status filters, affiliations, responsive table, pagination, and empty/privacy states |
| Community operations · Member profile | **Implemented in 7.3 milestone 2:** identity/contact presentation, supported ministry/choir affiliations, visibility-scoped attendance, responsive detail/edit layouts, and validation states |
| Community operations · Attendance workspace | **Implemented for the current domain in 7.3 milestone 4:** permission-scoped overview/history, event/date filters, real summary cards, responsive status table, active navigation, and refined per-event recording. Full active-member roster, guests, bulk actions, and export remain backend gaps. |
| Community operations · Giving records | **Implemented for the current domain in 7.3 milestone 4:** confidential filtered ledger, actual total/record/fund summaries, date/fund/method/search controls, fund management, contribution forms, metadata, and private member history. Reports, reconciliation, and export remain separate gaps. |
| Community operations · Ministry and volunteers | **Implemented for the current domain in 7.3 milestone 3:** searchable/status-aware team cards, leaders, protected membership roster, forms, visible ministry activities, responsive states, and permission-backed actions. Volunteer assignments/availability remain out of scope. |
| Scheduling & bookings · Event and resource calendar | **Implemented for existing events in 7.3 milestone 3:** upcoming/past/all directory, search/type/ministry filters, responsive event cards, visibility, registration/capacity/waitlist details, forms, cancellation, participants, and attendance. Week-grid resources, service requests, and bookings remain unsupported. |
| Scheduling & bookings · Booking details | Not implemented; no navigation added |
| Scheduling & bookings · Paid booking checkout | Not implemented; no navigation added |
| Scheduling & bookings · Confirmation and receipt | Not implemented; no navigation added |
| Worship planning · Song library | Existing screen inherits shell/tokens; detailed Figma screen work not started |
| Worship planning · Approved service plan | **Implemented for the current domain in 7.3 milestone 6:** scoped upcoming/previous directory, filters and summaries, preparation-state detail, linked events, ordered song setlist, choir participation, assignments, Spotify/resources, and refined forms. Generic service items, approval/version history, sharing, and conflicts remain backend gaps. |
| Worship planning · Post-service feedback | Not implemented; requires separate backend scope |
| Worship planning · Song recommendations | Reserved for Phase 8; not implemented and no navigation added |
| Song practice initial MOBILE view | Existing protected resources unchanged; specialized Inter/amber practice UI not started |
| Insights · Church reports | Reporting screen not started; no misleading route/navigation added |
| Member experience · Member portal | **Implemented in 7.3 milestone 1:** visible upcoming events, active ministry memberships, choir song assignments, account roles, permission-backed links, and unlinked-record empty state |
| Member experience · Notifications | Unified notifications not implemented; no navigation added |
| Member experience · Access and profile settings | Existing profile/account screens inherit shell/tokens; detailed tabs/preferences not started |

## Choir-management adaptation

**Implemented for the current domain in 7.3 milestone 5:** role-aware overview,
protected searchable roster, leader information, rehearsal timing/search/status
views, linked events, attendance privacy, announcements, song assignments,
Spotify links, and protected resources. The exported file has no dedicated
choir-management frame, so shared desktop patterns were used without inventing
missing design details.

## Shared implementation coverage

- [x] Official logo on authenticated and login layouts
- [x] Desktop sidebar and application header
- [x] Permission-backed navigation for real routes only
- [x] Active navigation state by current Django module
- [x] Responsive off-canvas navigation
- [x] Shared buttons, forms, cards, tables, pagination, alerts, and statuses
- [x] Skip link, focus visibility, and reduced-motion handling
- [x] Dashboard screen implementation: administrator overview and member portal
- [ ] Reports implementation
- [ ] Screen-by-screen Phase 7 refinement
- [ ] Specialized mobile practice design decision and implementation

See [[Phase-7-Figma-Design-Audit]], [[Design-System]], and [[Task-Tracker]].

## Phase 7.3 milestone 1 boundaries

- Dashboard content comes only from existing models and permission-scoped
  querysets; restricted event visibility is preserved.
- Giving totals render only for users with `giving.manage_giving`.
- Booking/payment metrics, care queues, charts without truthful source data,
  unified notifications, and reports were not simulated.
- The existing sidebar is the primary navigation implementation for this group.
- Responsive cards collapse to one column on small screens and metric cards to
  a compact two-column grid.

## Phase 7.3 milestone 2 boundaries

- The exported `static/assets/CHORD.svg` Member Directory and Member Profile
  regions were rendered locally and used as the primary visual references.
- Directory segments are derived from existing status and creation timestamps;
  ministry filtering uses active `MinistryMembership` records.
- Contact columns and contact search require
  `members.view_sensitive_member_data`.
- Attendance requires `events.view_eventparticipant` and is limited through
  `visible_events_for`; giving data never enters member profile context.
- Import/export, contact verification, volunteer availability, unsupported
  activity history, and care workflows were not presented as functional.

## Phase 7.3 milestone 3 boundaries

- The local `CHORD.svg` Ministry & Volunteers, Church Calendar, and Attendance
  regions were rendered and inspected without Figma MCP or source changes.
- Ministry leaders and membership rows reuse active `MinistryMembership`
  records; full rosters remain object-scoped to administrators and active
  assigned leaders.
- Ministry activity lists and event directories reuse `visible_events_for`;
  hidden events remain unavailable through direct detail URLs.
- Registration, capacity, waitlisting, cancellation promotion, and attendance
  continue through the existing event services and validated forms.
- Assignment conflicts, volunteer availability, service requests, rooms,
  resource booking, payments, full-member attendance, guest records, and
  export were not simulated because those domains do not exist.

## Phase 7.3 milestone 4 boundaries

- The local `CHORD.svg` Attendance and Giving Records regions were rendered and
  used as visual references without Figma MCP or source-design changes.
- Attendance overview/history aggregates existing non-cancelled
  `EventParticipant` rows and limits events through `manageable_events_for`,
  which composes existing visibility and ministry-leadership scope.
- Per-event attendance continues through `record_event_attendance`; no parallel
  roster, attendance model, or automatic attendance behavior was introduced.
- Giving totals and fund summaries are calculated only inside the existing
  authorized admin or member-self querysets. Member pages never receive donor,
  note, audit, or contribution data belonging to another member.
- Contribution create/update still uses the existing atomic audit services.
  Online payment, giving reports, export, reconciliation, tax receipts, and
  event-linked offerings were not simulated.

## Phase 7.3 milestone 5 boundaries

- No dedicated choir-management frame or searchable choir label exists in the
  exported `CHORD.svg`; the audited desktop shell, cards, tables, forms, status
  language, and documented mobile-practice boundary were the references.
- Choir overview, roster, rehearsals, attendance, announcements, and song
  assignment pages reuse existing models, permissions, and services. No choir
  model, song, resource, playback, or notification domain was duplicated.
- Worship Leaders may open schedule/roster coordination through their existing
  permissions, but announcements remain absent unless the account separately
  has the announcement-view permission.
- Choir Members receive only their own attendance and assignments. Protected
  song resources continue through the Phase 6 permission-checked routes.
- Automatic reminders, outbound communication, attendance export, practice
  controls, chord generation, and recommendation behavior were not simulated.

## Phase 7.3 milestone 6 boundaries

- The local Approved Service Plan frame was rendered from `CHORD.svg` without
  Figma MCP or source-design changes. Its layout informed the service heading,
  state banner, ordered setlist, team sidebar, and service summary.
- CHORD's status is preparation state, not approval. No approved-by identity,
  version number, sharing state, team notification, or conflict warning was
  fabricated.
- The order of service remains an ordered song setlist because generic prayer,
  message, offering, duration, and non-song service-item models do not exist.
- Plan directories and counts use the existing permission-scoped queryset;
  Choir Members still receive only participating plans and their own assignment
  names. Restricted linked events are not exposed as working direct links.
- Add, move, remove, participant synchronization, and song assignment continue
  through the existing atomic services and permissions.

The next recommended screen group is Song Library and Resources. Do not begin it without
explicit authorization.
