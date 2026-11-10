# Design Change Log

## 2026-11-09 - Phase 7.2 design system and shell foundation

- Added the audited forest-green, warm-neutral desktop tokens to a project-owned
  CSS layer while retaining Bootstrap 5.
- Replaced the dark top navbar with a 232 px permission-aware sidebar, 74 px
  application header, breadcrumb, profile shortcut, and shared main workspace.
- Added responsive drawer behavior below 992 px with a backdrop, Escape support,
  focus movement, and reduced-motion support.
- Added branded authentication treatment and reused one official horizontal PNG
  partial across login and the sidebar.
- Kept the mobile practice Inter/amber system isolated rather than merging two
  visual languages without a design decision.
- Omitted design-only Bookings, Recommendations, Reports, Notifications,
  multi-church switching, and global search from the functional shell.
- Used text navigation because the exact Figma icon assets are not durable local
  assets; no substitute icon set was invented.
- Added six application-shell regression tests. The full 113-test suite passed.
- Verified Django checks, migration consistency, Ruff lint, Ruff formatting,
  live server startup, and HTTP 200 responses for login, CSS, JavaScript, PNG,
  and SVG assets.
- Headless Chrome screenshot rendering could not run because the managed Windows
  session's GPU process was unavailable. No visual screenshot success is
  claimed; browser HTTP/static and Django rendering checks passed independently.

No Figma file, database model, migration, backend workflow, recommendation
feature, or Git commit was created.

See [[Design-System]], [[Branding-and-Assets]],
[[Screen-Implementation-Tracker]], and [[Development-Log]].

## 2026-11-09 - Phase 7.3 dashboard screen group

- Replaced the minimal greeting card with administrator and member dashboard
  compositions mapped from the audited Figma overview screens.
- Reused existing shell tokens and added responsive metric, panel, event-row,
  person-row, guidance-banner, role, and empty-state patterns.
- Kept dashboard actions functional and permission-backed; did not render dead
  controls for unsupported booking, notification, report, or ML features.
- Used real cross-module values and visibility-scoped querysets instead of mock
  chart data or placeholder operational totals.

See [[Screen-Implementation-Tracker]] and [[Development-Log]].

## 2026-11-10 - Phase 7.3 member-management screen group

- Used locally rendered crops of the combined exported `CHORD.svg` as the
  Member Directory and Member Profile references; no Figma MCP call was made.
- Added the designed directory hierarchy: heading, derived segment tabs,
  search/ministry/status controls, compact people table, pagination, privacy
  guidance, and truthful no-results state.
- Adapted the profile design into semantic detail and edit screens with identity
  fields, a member summary, active ministry/choir affiliations, recent visible
  attendance, and protected-record guidance.
- Reused shared tokens, panels, status pills, form controls, spacing, and
  avatars. On narrow screens the profile becomes one column and nonessential
  directory columns collapse while names, statuses, and actions remain.
- Omitted nonfunctional import/export, contact verification, availability,
  care, giving, and generic activity controls.

See [[Screen-Implementation-Tracker]], [[Development-Log]], and
[[../03-Modules/Member-Management]].

## 2026-11-10 - Phase 7.3 ministries and church-events screen group

- Used local rendered crops of the exported Ministry & Volunteers, Church
  Calendar, and Attendance designs; Figma MCP remained unused.
- Adapted the ministry reference's team cards and dense roster language to the
  existing Ministry/MinistryMembership domain. Unsupported assignment,
  coverage, availability, and conflict controls were omitted.
- Adapted the calendar reference into a responsive event directory because
  CHORD has real events but no rooms, service-request taxonomy, or booking
  engine. Upcoming/past tabs, filters, event cards, and capacity information
  all use live permission-scoped records.
- Refined event detail, registration, cancellation, participant, and attendance
  screens with shared panels, definition grids, tables, forms, statuses,
  guidance, and responsive layouts.
- Kept attendance limited to existing event participants. The designed full
  church roster, first-time guests, export, and bulk shortcuts were not
  presented as working features.

See [[Screen-Implementation-Tracker]], [[Development-Log]],
[[../03-Modules/Ministry-Management]], and
[[../03-Modules/Events-Attendance]].

## 2026-11-10 - Phase 7.3 attendance and giving screen group

- Reused local rendered Attendance and Giving Records references; no Figma MCP
  call or source-file modification occurred.
- Translated the Attendance composition into a permission-scoped history and
  event-recording flow backed only by current event participants. Replaced the
  unsupported full-roster/guest/export controls with truthful scope guidance.
- Translated Giving Records into actual filtered totals, confidential ledger
  rows, fund categories, manual contribution forms, and a private member view.
  Omitted design-only service linkage, reconciliation, reports, and export.
- Reused the established metric cards, panels, form controls, tables, badges,
  guidance banners, pagination, sidebar, and responsive breakpoints; added only
  attendance/giving layout styles not already expressed by shared components.
- Preserved text-based statuses and semantic labels so meaning is not conveyed
  by color alone. Dense secondary columns collapse on small screens while core
  event, donor/fund, amount, and action information remains available.

See [[Screen-Implementation-Tracker]], [[Development-Log]],
[[../03-Modules/Events-Attendance]], and [[../03-Modules/Giving]].
