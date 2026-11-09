# Screen Implementation Tracker

**Phase 7.3 milestone 1 result:** Dashboard screen group complete. The shared
shell remains the Phase 7.2 foundation; other Figma screens remain separate
milestones.

Every existing authenticated Django screen now inherits the role-aware shell,
header, responsive drawer, design tokens, and shared Bootstrap refinements from
`base.html`. This does not mean the 19 Figma screens are individually complete.

| Figma screen | Current implementation status |
| --- | --- |
| Community operations · Admin overview | **Implemented in 7.3 milestone 1:** permission-scoped metrics, quick actions, upcoming events, recent members, worship preparation, and confidential monthly giving summary |
| Community operations · Member directory | Shell/tokens applied to existing list; Figma-specific composition not started |
| Community operations · Member profile | Shell/tokens applied to existing detail/edit views; tabbed composition not started |
| Community operations · Attendance workspace | Existing event attendance retained; advanced roster/guest design remains a backend gap |
| Community operations · Giving records | Existing screens inherit shell/tokens; aggregate cards/export not started |
| Community operations · Ministry and volunteers | Existing screens inherit shell/tokens; availability/assignment features remain out of scope |
| Scheduling & bookings · Event and resource calendar | Existing event routes inherit shell/tokens; calendar-grid and resource booking are not implemented |
| Scheduling & bookings · Booking details | Not implemented; no navigation added |
| Scheduling & bookings · Paid booking checkout | Not implemented; no navigation added |
| Scheduling & bookings · Confirmation and receipt | Not implemented; no navigation added |
| Worship planning · Song library | Existing screen inherits shell/tokens; detailed Figma screen work not started |
| Worship planning · Approved service plan | Existing plan screen inherits shell/tokens; approval/version features remain a gap |
| Worship planning · Post-service feedback | Not implemented; requires separate backend scope |
| Worship planning · Song recommendations | Reserved for Phase 8; not implemented and no navigation added |
| Song practice initial MOBILE view | Existing protected resources unchanged; specialized Inter/amber practice UI not started |
| Insights · Church reports | Reporting screen not started; no misleading route/navigation added |
| Member experience · Member portal | **Implemented in 7.3 milestone 1:** visible upcoming events, active ministry memberships, choir song assignments, account roles, permission-backed links, and unlinked-record empty state |
| Member experience · Notifications | Unified notifications not implemented; no navigation added |
| Member experience · Access and profile settings | Existing profile/account screens inherit shell/tokens; detailed tabs/preferences not started |

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

The next recommended group is Member Directory and Member Profile refinement.
