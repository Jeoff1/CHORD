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
