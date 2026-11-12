# Development Log

## 2026-11-06 — pre-development setup

- Inspected the existing Django 6.1 bootstrap and preserved its files.
- Found Python 3.14.7; Python 3.12 is not installed.
- Verified PostgreSQL 17.11 service and local port 5432.
- Confirmed PostgreSQL administration requires a password, so no database or
  role was changed.
- Created `.venv`; installed Django 5.2.19 LTS and requested tools.
- Reconfigured Django for environment-driven PostgreSQL access and Manila time.
- Added `accounts.User` before any PostgreSQL migrations and generated its
  initial migration.
- Added tests, Ruff configuration, Git repository files, and this vault.
- Passed two settings-only tests, Django checks, dependency validation, Ruff
  lint, Ruff formatting, and migration-drift validation.
- Confirmed migrations, the full three-test suite, and server startup are
  blocked specifically by the intentionally unset PostgreSQL password.

## 2026-11-06 — PostgreSQL completion verification

- Confirmed `.env` contains credentials without displaying them.
- Connected to `chord_db` as `chord_user` on PostgreSQL 17.11.
- Verified Django resolves the custom model as `accounts.User` before migration.
- Applied all initial migrations and verified 10 tables, including
  `accounts_user`, `django_migrations`, and `django_session`.
- Passed dependency, migration-drift, Django system, Ruff lint, and Ruff format
  checks.
- Started the development server and received HTTP 200 at `127.0.0.1:8000`.
- The full test suite found three tests but could not create `test_chord_db`
  because `chord_user` lacks `CREATEDB`; documented the minimal pgAdmin fix.
- Granted `chord_user` the local `CREATEDB` capability through pgAdmin.
- Reran all three tests successfully against an isolated PostgreSQL test
  database and confirmed Django removed `test_chord_db` afterward.
- Repeated system, migration-drift, dependency, Ruff lint, and Ruff format
  checks; all passed. The environment is ready for master development.

See [[Known-Issues]] and [[../04-Testing/Environment-Verification]].

## 2026-11-06 — Phase 3 member management

- **Phase:** 3
- **Task:** Privacy-aware member record management.
- **Files:** Created `apps/members/`, templates, migration `0001`, and Phase 3
  tests; updated permission synchronization, navigation, URLs, and vault notes.
- **Implementation:** Added member records, optional account linking, status,
  contact/date validation, search/filtering, self-record access, scoped
  sensitive fields, account management workflows, and audit events.
- **Security:** UUID URLs, server-side object access, separate sensitive-data
  permission, email-search restriction, no delete permission/workflow, and audit
  logs containing field names rather than confidential values.
- **Tests:** 32 combined tests passed. System, migration-drift, dependency, Ruff
  lint/format, schema/permission, and server route checks passed.
- **Refactoring:** Smoke testing found and fixed anonymous 403 behavior while
  preserving authenticated-denial 403 responses.
- **Problems:** The first smoke-test request returned 403 instead of a login
  redirect; fixed and covered by regression test.
- **Next:** Stop at the phase boundary. Ministry management is recommended next
  only after authorization.

See [[../03-Modules/Member-Management]], [[Refactoring-Log]], and
[[../04-Testing/Phase-3-Test-Results]].

## 2026-11-06 — Phase 2 authentication and RBAC

- **Phase:** 2
- **Task:** Authentication, profiles, account management, and multi-role RBAC.
- **Files:** Updated `config/settings.py`, `config/urls.py`, the accounts app,
  README, templates, migration `0002`, tests, and this vault.
- **Implementation:** Added six seeded roles, `Role`, `UserRole`, `Profile`, a
  role-permission backend, secure login/POST logout, password changes,
  self-profile editing, and permission-protected account administration.
- **Security:** Church Administrator is not a superuser and receives only Phase
  2 account permissions. Inactive users receive no role permissions. Users
  cannot deactivate themselves or change their own roles through the UI.
- **Tests:** 17 Django tests passed. Django checks, migration drift, dependency
  checks, Ruff lint, Ruff formatting, and server login/redirect smoke checks
  passed.
- **Refactoring:** Corrected form save ordering so every role assignment created
  through account management retains its `assigned_by` audit record.
- **Problems:** One audit test initially failed and drove the save-order fix.
- **Next:** Stop at the phase boundary. Begin member management only after user
  authorization.

See [[../03-Modules/Authentication]], [[Refactoring-Log]], and
[[../04-Testing/Phase-2-Test-Results]].

## 2026-11-06 — Initial administrator bootstrap

- **Phase:** 2 follow-up
- **Task:** Bootstrap and verify the first administrator.
- **Implementation:** The user created a local Django superuser and assigned the
  Church Administrator role through Django admin.
- **Verification:** Confirmed one active Church Administrator assignment, one
  superuser, and a clean Django system check without displaying account details.
- **Next:** Optionally create a separate non-superuser Church Administrator for
  routine use; keep the superuser for framework administration and recovery.

## 2026-11-07 — Comprehensive Phases 1–3 QA audit

- **Phase:** Pre-Phase 4 quality gate
- **Task:** Verify implementation, database architecture, security, features,
  tests, and documentation against the actual repository.
- **Files:** Reviewed all source, templates, migrations, settings, root files,
  and vault notes. Updated permissions, validators, settings, templates, tests,
  README, migration `accounts.0003`, and audit documentation.
- **Refactoring:** Tightened action permissions, made role synchronization
  authoritative, shared phone validation, removed an unused join, and added
  reusable pagination plus secure production environment switches.
- **Security:** Added CSRF/HTTP-method regressions, mutation-denial tests, stale
  permission removal, production `check --deploy` simulation, and secret-ignore
  verification.
- **Database:** PostgreSQL introspection confirmed required tables, unique
  constraints, one-to-one linkage, UUID uniqueness, and member indexes.
- **Tests:** Expanded from 32 to 44; all passed. Django checks, migration drift,
  dependency validation, Ruff lint/format, and live server smoke checks passed.
- **Issues:** No critical issue. Git has no baseline commit, role removals lack a
  durable application audit event, and login rate limiting remains a production
  hardening item.
- **Next:** Review and create a Git baseline commit, then begin Phase 4 only when
  explicitly authorized.

See [[../04-Testing/Phases-1-3-QA-Audit]], [[Known-Issues]], and
[[Refactoring-Log]].

## 2026-11-08 - Phase 4 choir and worship management

- **Phase:** 4
- **Task:** Choir enrollment and activity, worship song library, and service
  planning.
- **Files:** Added `apps/worship/`, 18 worship templates, migration `0001`, 25
  Phase 4 tests, protected-resource storage, scoped role mappings, navigation,
  and vault documentation.
- **Choir:** Added member enrollment, voice parts, status, rehearsals,
  attendance, announcements, activity information, and member assignments.
- **Songs:** Added searchable/filterable/sortable metadata, normalized themes,
  categories, key/tempo, usage history, and authorization-tracked chord/lead
  sheet resources.
- **Planning:** Added service plans, preparation status, choir participation,
  ordered setlists, transactional movement/removal, and member assignments.
- **Security:** Enforced responsibility permissions and participant-level
  querysets; protected attendance, assignments, plan usage, and licensed files.
- **Database:** Applied `worship.0001_initial`; verified all 10 tables plus key
  unique constraints and authoritative role permissions in PostgreSQL.
- **Tests:** Added 25 Phase 4 tests. The complete 69-test suite passed along
  with system checks, migration drift, dependency validation, Ruff lint, and
  Ruff formatting.
- **Refactoring:** Added concurrency row locks, protected file storage, generic
  filter-preserving pagination, deferred protected-object lookup, and privacy
  filtering after implementation review.
- **Boundary:** No event module, Phase 5 feature, or ML engine was implemented.
- **Next:** Review Phase 4 changes and explicitly authorize/scope Phase 5.

See [[../03-Modules/Choir-Worship-Management]],
[[../04-Testing/Phase-4-Test-Results]], [[Known-Issues]], and
[[Refactoring-Log]].

## 2026-11-09 - Phase 5 core modules and integration

- **Audit:** Compared the implemented Phase 1-4 source and vault against the
  documented requirements. Confirmed ministry, church-wide events/attendance,
  and giving were the remaining core gaps; Phase 4 song metadata was already
  suitably structured for future use.
- **Roadmap:** Adopted the nine-phase sequence. Machine learning is reserved
  exclusively for Phase 8 and remains unimplemented.
- **Ministries:** Added ministry lifecycle, memberships, leadership, directory,
  and role-plus-object authorization.
- **Events:** Added audience-aware schedules, registration, capacity/waitlist,
  attendance, and assigned-ministry management.
- **Integration:** Added optional event links to worship plans/rehearsals and
  canonical schedule synchronization without changing existing records.
- **Giving:** Added funds, confidential contribution recording, audit metadata,
  and linked-member self-history.
- **Database:** Applied `ministries.0001`, `events.0001`, `events.0002`,
  `giving.0001`, and `worship.0002` to PostgreSQL.
- **Security:** Added authoritative permissions for all six roles, queryset
  audience filtering, object-level leadership checks, scoped attendance forms,
  and giving isolation.
- **Tests:** Added 25 tests; all 94 tests passed. Django checks, migration drift,
  Ruff lint/format, and server verification passed.
- **Refactoring:** Fixed unsaved-instance filtering in optional Phase 4 event
  selectors and promoted waitlisted registrants transactionally on cancellation.
- **Boundary:** Phase 6 was not started. No ML dependency, model, algorithm,
  endpoint, ranking, or interface was added.

See [[../03-Modules/Ministry-Management]],
[[../03-Modules/Events-Attendance]], [[../03-Modules/Giving]], and
[[../04-Testing/Phase-5-Test-Results]].

## 2026-11-09 - Phase 6 song resources and chord sheets

- **Audit:** Reused the Phase 4 `Song`, `SongResource`, private storage,
  resource permissions, setlists, assignments, and rehearsal workflows.
- **Spotify:** Added strict track URL/URI/ID normalization and the official
  Spotify track iframe with a normal-link and availability fallback.
- **Viewing:** Added permission-checked PDF/image streaming, escaped UTF-8 text,
  safe basic ChordPro display, and unsupported-format download guidance.
- **Management:** Added resource editing/replacement, post-commit old-file
  cleanup, latest-updater metadata, and ChordPro file extensions.
- **Integration:** Added resources to setlists, assignments, and rehearsal
  preparation; rehearsals now select existing songs.
- **Security:** Kept files outside public media, enforced the existing view
  permission, fixed response content types, added `nosniff`, and never renders
  uploaded text as trusted HTML.
- **Database:** Applied and introspected `worship.0003`; confirmed the song ID,
  resource audit columns, rehearsal-song table, and update permissions.
- **Tests:** Added 13 tests; all 107 tests passed in 57.301 seconds. Checks,
  migration drift, dependencies, Ruff, and server smoke passed.
- **Boundary:** Phase 7 was not started. No ML behavior or dependency was added.

See [[../03-Modules/Song-Resources-Chord-Sheets]] and
[[../04-Testing/Phase-6-Test-Results]].

## 2026-11-09 - Phase 7 Figma design audit

- **Scope:** Performed a read-only pre-implementation audit of the CHORD Initial
  Design through the authenticated Figma MCP server. No Figma or frontend
  changes were made.
- **Inventory:** Identified 19 top-level frames covering administration,
  members, attendance, giving, ministries, events/calendar, bookings, songs,
  service plans, reports, member experience, access/profile, and a mobile song
  practice experience.
- **Design system:** Documented the Lato/forest-green desktop system, the
  distinct Inter/amber mobile practice system, the repeated sidebar/workspace
  shell, component patterns, and the visually matching local CHORD logo assets.
- **Source comparison:** Mapped all screens to actual Django apps, URLs, models,
  permissions, and templates. Confirmed strong reuse opportunities for members,
  ministries, events, giving, choir, songs, resources, and worship plans.
- **Gaps:** Documented that bookings/payments/receipts, unified notifications,
  volunteer availability, guest/full-roster attendance, plan approval/version
  history, post-service feedback, multi-church behavior, and advanced practice
  controls are not implemented backend capabilities.
- **ML boundary:** The Figma Recommendations screen is reference only. Phase 8
  remains reserved and no recommendation UI, endpoint, ranking, or algorithm
  was implemented.
- **Verification note:** Metadata covered all 19 frames and screenshots/design
  context covered 18; the Figma Starter MCP call cap prevented the final Member
  Directory screenshot, whose structure and source mapping were still verified.
- **Status:** Phase 7 implementation has not started. No tests or automated code
  checks were run because this task changed documentation only.

See [[Phase-7-Figma-Design-Audit]], [[Task-Tracker]], and [[Known-Issues]].

## 2026-11-09 - Phase 7.2 design system and application shell

- **Branding:** Validated the official PNG/SVG files and integrated the exact
  horizontal PNG through Django staticfiles on login and authenticated layouts.
- **Design system:** Added reusable forest-green/warm-neutral tokens and shared
  styling for typography, spacing, radii, shadows, buttons, forms, cards,
  tables, pagination, alerts, and statuses.
- **Shell:** Replaced the dark Bootstrap navbar with the audited desktop sidebar,
  application header, breadcrumb, current-section state, identity, and shared
  content workspace.
- **Authorization:** Navigation remains permission-based and links only to real
  routes. Bookings, Recommendations, Reports, and Notifications were not added.
- **Responsive/accessibility:** Added an off-canvas mobile drawer, backdrop,
  Escape handling, focus movement, skip link, focus-visible states, and reduced
  motion handling.
- **Architecture:** Added a presentation-only context processor and reusable
  shell partials; no model, migration, or backend workflow changed.
- **Tests:** Added six shell tests. All 113 tests passed in 60.597 seconds using
  the isolated PostgreSQL test database. Django checks, migration consistency,
  Ruff lint, and Ruff formatting passed.
- **Smoke:** The development server started cleanly. Login, CSS, JavaScript, PNG,
  and SVG requests returned HTTP 200 with correct content types.
- **Limitation:** Headless Chrome screenshots failed because its GPU process is
  unavailable in the managed Windows session. No screenshot verification is
  claimed.
- **Boundary:** Individual Figma screens and reports were not implemented. No
  Phase 8 recommendation behavior or UI was added. No Git commit was created.

See [[Design-System]], [[Branding-and-Assets]],
[[Screen-Implementation-Tracker]], and [[Design-Change-Log]].

## 2026-11-09 - Phase 7.3 milestone 1 dashboard screens

- **Screens:** Implemented the Community Operations administrator overview and
  Member Experience member portal on the existing `accounts:dashboard` route.
- **Administrator experience:** Added real member, event, ministry, worship-plan,
  and permission-protected monthly giving summaries; upcoming calendar, recent
  member, service-preparation, and functional quick-action panels.
- **Member experience:** Added visibility-scoped upcoming events, active ministry
  memberships, upcoming choir song assignments, role summary, functional links,
  and an honest unlinked-member-record state.
- **Design:** Reused the audited Lato/forest-green system, cards, status pills,
  spacing, and responsive shell. Added reusable dashboard panel, metric, event,
  person, guidance, and empty-state styles plus a shared event-list partial.
- **Security:** Reused `visible_events_for`; giving totals require
  `giving.manage_giving`; all links remain permission-backed. Restricted events
  and administrator financial summaries are covered by tests.
- **Tests:** Added three dashboard tests. Dashboard/shell tests passed 9/9 and
  the full PostgreSQL suite passed 116/116 in 60.766 seconds. Django checks,
  migration consistency, Ruff lint, and Ruff formatting passed.
- **Boundary:** Did not add bookings, payments, care workflows, notifications,
  reports, fake charts, or recommendations. No Figma source was modified and no
  new MCP audit was performed.

See [[Screen-Implementation-Tracker]] and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-10 - Phase 7.3 milestone 2 member management

- **References:** Rendered the Member Directory and Member Profile regions from
  the user-provided combined `static/assets/CHORD.svg`. The source export was
  not modified or embedded as application UI.
- **Directory:** Added derived All/Active/New/Inactive segments, authorized
  name/email/phone search, active-ministry and status filters, filter-preserving
  pagination, membership/choir affiliations, status pills, responsive columns,
  and explicit privacy/empty states.
- **Profile:** Refined detail and create/edit presentation with shared form
  fields, identity/contact details, member summary, active ministry and choir
  affiliations, and recent attendance restricted to permitted visible events.
- **ORM/refactoring:** Centralized the profile queryset/context, selected linked
  account/choir relations, prefetched active ministry memberships and account
  roles, and selected attendance events to prevent template N+1 queries.
- **Security:** Preserved directory, sensitive-data, create, and change
  permissions. Limited viewers receive no contact columns/search results;
  attendance reuses event visibility; no giving query or value is exposed.
- **Tests:** Added seven member UI/query/privacy tests. All 26 member tests and
  nine dashboard/shell regressions passed. The full PostgreSQL suite passed
  123/123 in 58.218 seconds. Django checks, migration consistency, Ruff lint,
  and Ruff formatting passed.
- **Visual verification:** Headless Chrome successfully rendered the two local
  SVG reference crops. Authenticated application screenshot comparison was not
  automated; responsive behavior is verified structurally and remains suitable
  for a manual browser pass.
- **Boundary:** No model, migration, booking/payment, notifications, care,
  advanced attendance, recommendation, or Figma-file changes were introduced.

See [[Screen-Implementation-Tracker]], [[Design-Change-Log]],
[[../03-Modules/Member-Management]], and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-10 - Phase 7.3 milestone 3 ministries and church events

- **References:** Rendered the Ministry & Volunteers, Church Calendar, and
  Attendance regions from the combined local `static/assets/CHORD.svg`; no
  Figma MCP call or source-design change was made.
- **Ministries:** Added responsive searchable team cards, administrator status
  filtering, active leaders/member counts, ministry purpose/status, visible
  upcoming activities, protected membership roster, and refined create/edit
  and enrollment forms.
- **Events:** Added upcoming/past/all segments, truthful filtered counts,
  search/type/ministry controls, responsive event cards, lifecycle/audience
  presentation, capacity and waitlist summaries, linked schedule details,
  registration/cancellation UI, participant forms, and attendance workspace.
- **Security:** Preserved `can_manage_ministry`, `can_manage_event`, and
  `visible_events_for`. General ministry viewers receive no roster; hidden
  events remain 404; management actions render only with their existing
  permissions.
- **ORM/refactoring:** Prefetched active ministry leaders, selected membership
  relations, annotated event registration/waitlist totals, selected linked
  worship/rehearsal records, and added deterministic list ordering.
- **Tests:** Added six UI/security/integration tests. Ministry/event tests passed
  23/23, the dashboard/shell/member/ministry/event regression set passed 58/58,
  and the full PostgreSQL suite passed 129/129 in 61.596 seconds. Django checks,
  migration consistency, Ruff lint, Ruff formatting, and diff checks passed.
- **Visual limitation:** Local SVG references were rendered successfully.
  Authenticated application desktop/mobile screenshot comparison was not
  automated and remains appropriate for a manual browser pass.
- **Boundary:** Volunteer assignments/availability, conflicts, church service
  requests, resource booking, payments, guest/full-roster attendance, exports,
  notifications, reports, and recommendations were not implemented.

See [[Screen-Implementation-Tracker]], [[Design-Change-Log]],
[[../03-Modules/Ministry-Management]], [[../03-Modules/Events-Attendance]], and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-10 - Phase 7.3 milestone 4 attendance and giving

- **References:** Rendered the Attendance and Giving Records regions from the
  combined local `static/assets/CHORD.svg`; no Figma MCP call or source-design
  change was made.
- **Attendance:** Added a real overview/history route with manageable-event and
  date filters, participant/present/absent/not-recorded summaries, responsive
  event rows, role-aware navigation, and a refined per-event recording screen.
  It aggregates the existing `EventParticipant` records and continues to save
  through `record_event_attendance`.
- **Giving:** Added confidential donor/fund/reference search, fund/method/date
  filters, filtered financial summary cards, fund totals, protected ledger
  metadata, refined contribution/fund forms, and private member-scoped giving
  totals/history.
- **Security:** Added `manageable_events_for` by composing existing visibility
  and leadership scope. Giving aggregates execute only on administrator or
  member-self querysets; contribution create/update remains permission-backed
  and atomic with field-name-only audit events.
- **ORM/refactoring:** Annotated attendance and fund totals, selected giving
  relationships, retained filter-preserving pagination, and reused shared form,
  metric, panel, table, status, and empty-state components.
- **Tests:** Added eight authorization/filter/summary tests and extended shell
  navigation coverage. Targeted attendance/giving/shell tests passed 35/35,
  the milestone regression set passed 64/64, and the full PostgreSQL suite
  passed 137/137 in 63.357 seconds. Checks, migration consistency, Ruff, and
  diff validation passed.
- **Visual limitation:** Exported SVG crops rendered successfully. Authenticated
  desktop/mobile application screenshots were not automated and remain a
  manual browser follow-up.
- **Boundary:** No full-member or guest attendance, export, reconciliation,
  online payment, tax receipt, giving report, notification, booking, care, or
  recommendation feature was introduced.

See [[Screen-Implementation-Tracker]], [[Design-Change-Log]],
[[../03-Modules/Events-Attendance]], [[../03-Modules/Giving]], and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-10 - Phase 7.3 milestone 5 choir management

- **References:** Reused the exported `static/assets/CHORD.svg`, the completed
  audit, and the Phase 7.2 desktop system. The export contains no dedicated
  choir-management frame or searchable choir text, so no missing composition
  was invented and Figma MCP remained unused.
- **Overview and roster:** Added real enrollment/rehearsal/announcement/
  assignment summaries, leader context, protected roster filters, voice/status
  presentation, pagination, and refined enrollment management.
- **Rehearsals:** Added upcoming/previous/all segmentation, search and status
  filters, deterministic ordering, linked-event context, selected songs,
  Spotify/resource access, attendance summaries, and responsive forms.
- **Announcements and assignments:** Added audience/publication management
  filters, responsive announcement details, and an assignment form limited to
  active worship-plan participants with existing practice resources.
- **Security:** Choir Members continue to receive only their own attendance and
  assignments. Worship Leaders can use their existing schedule/roster
  permissions but receive no announcement content without that permission.
- **ORM/refactoring:** Selected linked events, prefetched rehearsal songs and
  resources, aggregated roster/timing counts, added deterministic pagination,
  styled shared form widgets once, and removed redundant local render imports.
- **Tests:** Worship/resource/dashboard/shell regressions passed 53/53 in
  31.327 seconds; the protected rehearsal resource recheck passed 2/2; and the
  complete PostgreSQL suite passed 143/143 in 71.098 seconds. Django checks,
  migration consistency, Ruff, and diff validation passed.
- **Visual limitation:** With no dedicated choir frame, verification is against
  the established shared tokens and responsive structure. Authenticated
  desktop/mobile screenshot comparison remains a manual follow-up.
- **Boundary:** No notification service, custom playback, advanced practice
  controls, chord generation, new choir domain, or recommendation behavior was
  introduced.

See [[Screen-Implementation-Tracker]], [[Design-Change-Log]],
[[../03-Modules/Choir-Worship-Management]], and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-10 - Phase 7.3 milestone 6 worship planning

- **References:** Rendered the Approved Service Plan region from the local
  exported `static/assets/CHORD.svg`; no Figma MCP call or source-design change
  was made.
- **Directory and detail:** Added permission-scoped upcoming/previous/all
  segments, search and status filters, live plan summaries, responsive cards,
  preparation-state guidance, linked visible events, and a structured service
  detail layout.
- **Setlists and participation:** Refined the ordered song set with key, tempo,
  category, themes, notes, assignments, Spotify, protected resources, and the
  existing move/remove controls. Choir participation and assignments retain
  their existing privacy scope.
- **Forms:** Refined service-plan and existing-song forms using shared design
  components while preserving event-derived scheduling, transactional
  participant updates, validation, and current routes.
- **Security:** Administrators and Worship Leaders retain management access;
  Choir Leaders and participating Choir Members retain their established
  object-level access. Ordinary users are denied direct plan access, and a
  linked event is exposed only when its visibility rules allow it.
- **ORM/refactoring:** Selected creator/event relations, prefetched setlists,
  songs, resources, participants, and assignments, annotated directory counts,
  applied deterministic ordering, and consolidated repeated widget styling.
- **Tests:** Worship-planning/resource tests passed 16/16 in 20.322 seconds;
  worship/choir/dashboard/shell regressions passed 59/59 in 43.554 seconds;
  and the complete PostgreSQL suite passed 149/149 in 85.690 seconds.
- **Visual limitation:** The exported SVG reference was rendered locally.
  Authenticated desktop/mobile application screenshot comparison remains an
  appropriate manual browser follow-up.
- **Boundary:** Generic order-of-service items, per-item durations, approval
  and version history, plan sharing/notifications, worship-team positions,
  conflict detection, post-service feedback, and recommendation behavior were
  not implemented.

See [[Screen-Implementation-Tracker]], [[Design-Change-Log]],
[[../03-Modules/Choir-Worship-Management]], and
[[../04-Testing/Phase-7-Test-Results]].

## 2026-11-13 - Phase 7A ticket 01: Church Profile and Traditions

- Planned Phase 7A (multi-tradition support) and paused remaining Phase 7
  screens. See [[../01-Project/Multi-Tradition-Support]].
- Added `apps.traditions` with Tradition presets, the singleton Church
  Profile, the tradition-config service, and the administrator-only
  `/church/` screen; the shell shows the active church and Tradition.
- Built test-first at the agreed seams (Django test client and the
  tradition-config service): 9 new tests.
- Two-axis code review: fixed the singleton race (data migration plus
  `get_or_create`), blocked admin add/delete, required the matching change
  permission, and added tests for data kept on switch.
- Verification: full suite, PostgreSQL, Ruff lint/format, migration check.

See [[../03-Modules/Church-Profile-Traditions]].
