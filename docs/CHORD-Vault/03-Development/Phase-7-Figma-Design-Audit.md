# Phase 7 Figma Design Audit

**Audit date:** 2026-11-09  
**Figma file:** [CHORD Initial Design](https://www.figma.com/design/Y6D6hKzHPoK3zDvDypCgg5/CHORD-Initial-Design?node-id=0-1)  
**Scope:** Read-only pre-implementation design audit and screen-to-module mapping  
**Implementation status:** Phase 7 frontend work has not started

## Boundary and evidence

- The Figma MCP connection was authenticated and the file was inspected without
  modifying it.
- The root page contains 19 top-level screen frames. Metadata was read for all
  19 frames and screenshots/design context were inspected for 18. The Figma
  Starter MCP call cap was reached on the final Member Directory screenshot;
  its frame metadata was still available and its Django mapping was verified
  from the source code.
- The Django comparison covered the installed apps, URL configurations, models,
  views, permissions, templates, current dashboard, shared base template, and
  existing branding assets.
- No Figma nodes, Django frontend files, models, migrations, or application
  behavior were changed during this audit.
- The Recommendations design is product reference for the reserved Phase 8. It
  is not approved Phase 7 scope and remains unimplemented.

## Design system findings

### Desktop application shell

The desktop screens consistently use a 1440 px canvas with:

- a fixed 232 px left navigation rail;
- a 74 px top utility bar;
- a warm off-white workspace (`#f6f5f0`);
- a light neutral sidebar (`#eeeee6`) and utility surface (`#fbfaf7`);
- dark forest green primary actions and active navigation (`#285744`);
- deep green body text (`#233a32`), muted text (`#748078`), light borders
  (`#dfe4dc`), pale green states (`#e9f0e9`), and white cards;
- Lato Regular and Bold for the desktop interface;
- compact 10-14 px navigation, metadata, and body text, with larger page and
  metric headings;
- 32 px workspace padding, compact 7-8 px control radii, larger card radii,
  thin borders, and little or no decorative shadow.

The repeated shell contains the CHORD identity, church workspace selector,
role-specific primary navigation, signed-in identity, breadcrumb, search,
date, notification icon, and profile avatar. The visual language is calm,
pastoral, data-dense, and substantially lighter than the current dark Bootstrap
navbar.

### Mobile practice experience

The single mobile frame is 430 px wide and deliberately distinct:

- warm cream background (`#f8f5ee`);
- near-black text (`#292820`), muted taupe (`#827d71`), amber chord/accent
  color (`#a26420`), and light divider (`#e5dfd3`);
- Inter typography rather than Lato;
- 26 px horizontal gutters;
- a large chord-and-lyric reading surface, rounded tuning panel, and persistent
  practice controls.

This may be an intentional focused “practice room” mode, but the type and color
shift should be confirmed before implementation so it does not become an
accidental second design system.

### Logo and identity

The Figma sidebar uses the green CHORD wordmark with a pale sage circle and a
church/steeple illustration integrated into the central letterform. The design
also expands the acronym as “Church Hub for Organized Resources and Devotion.”

The repository already contains visually matching branding assets at
`static/assets/branding/CHORD_Logo.png` and
`static/assets/branding/CHORD Logo.svg`. The current `base.html` does not use
them; it renders a text-only `CHORD` navbar brand. Visual matching was
confirmed, but the Figma asset and local file were not compared byte-for-byte.
The entire local `static/` directory is currently untracked by Git, so these
assets must be reviewed and committed before a deployment can rely on them.

### Repeated component patterns

The file consistently reuses these visual patterns:

- role-aware sidebar navigation items and active states;
- utility bar, breadcrumb, initials avatar, and signed-in identity;
- page heading with primary and secondary actions;
- cards/panels, metric cards, status pills, guidance banners, and dividers;
- tabs, search/filter controls, compact tables, pagination, and side summaries;
- empty/guidance copy, warning states, and permission-sensitive explanations;
- green primary buttons, bordered secondary buttons, and textual arrow links.

The inspected Figma node returned no variable definitions, and metadata
represented the repeated patterns as frames rather than clear component
instances. Phase 7 should therefore establish a small local CSS token layer and
reusable Django template partials instead of assuming a published Figma token or
component library already exists.

## Navigation analysis

The administrator navigation shown in Figma includes Overview, Members,
Attendance, Giving records, Ministries & volunteers, Calendar, Bookings, Song
library, Recommendations, Service plans, Reports, Notifications, and Access &
profile. Member screens reduce this to My community, Calendar, My bookings,
Notifications, and Access & profile. Worship screens expose the subset relevant
to worship leadership.

CHORD already computes server-side permissions for each implemented module, so
the visual shell can eventually remain role-aware without hard-coding role
names. Navigation must continue to be generated from permissions, and absent
features must not receive placeholder links that imply they work.

Current navigation is a single Bootstrap 5 dark top navbar in `base.html`.
There is no sidebar shell, utility bar, global search, notification badge,
church selector, or responsive navigation treatment matching Figma.

## Screen-to-module mapping

| Figma screen | Existing Django target | Fit | Verified gap or boundary |
| --- | --- | --- | --- |
| Community operations · Admin overview | `accounts:dashboard` plus data from members, events, giving, ministries, and worship | Low | Current dashboard only greets the user and lists roles. Aggregate cards, care queue, chart, and cross-module panels are Phase 7 work. Booking metrics are not backed by a booking domain. |
| Community operations · Member directory | `members:list`, `members:detail` | Strong partial | Search, pagination, UUID detail URLs, and privacy permissions exist. Figma composition, compact status treatment, and integrated side detail require UI work. |
| Community operations · Member profile | `members:detail`, `members:edit`, `members:my-record` | Strong partial | Core identity/contact and status exist. One composed tabbed view of ministries, attendance history, and activity is not implemented. Sensitive fields must remain permission-scoped. |
| Community operations · Attendance workspace | `events:attendance`, `EventParticipant` | Partial | Attendance is stored per registered participant. There is no automatic full active-member roster, first-time guest model, bulk roster workflow, or export matching the design. |
| Community operations · Giving records | `giving:contribution-list`, contribution/fund forms, `giving:my-contributions` | Partial | Confidential manual records and audit metadata exist. Aggregate report cards and ledger export are intentionally Phase 7 work; booking revenue must remain separate. |
| Community operations · Ministry and volunteers | `ministries:list`, `ministries:detail`, membership forms | Partial | Teams, members, leaders, and object permissions exist. Volunteer assignments, availability requests, coverage, and conflict detection do not. |
| Scheduling & bookings · Event and resource calendar | `events:list`, `events:detail`, registration/attendance, linked worship plans and rehearsals | Partial | Event scheduling and registration exist. The current UI is a list, not a calendar grid. Resource/room availability, service-request taxonomy, recurrence, and booking approval do not exist. |
| Scheduling & bookings · Booking details | No booking model; `events:detail` is only a conceptual neighbor | None | Reserved resources, requester approval, fees, capacity checks, and payment status require a separately authorized backend scope. |
| Scheduling & bookings · Paid booking checkout | No payment or booking implementation | None | GCash/card/manual checkout, payment verification, and fee processing are design-only. Do not collect payment credentials from this mockup. |
| Scheduling & bookings · Confirmation and receipt | No receipt/booking implementation | None | Receipt numbers, paid status, downloads, and booking calendar actions need an approved booking/payment domain and security review. |
| Worship planning · Song library | `worship:song-list`, song detail/forms/resources | Strong partial | Title, artist, key, BPM, category, themes, search/filter/sort, Spotify, protected resources, and usage history exist. Favorites, ratings, bulk import, and the exact tab/side-panel behaviors do not. |
| Worship planning · Approved service plan | `worship:plan-detail`, plan/setlist/assignment forms | Partial | Status, ordered songs, keys, choir participation, assignments, and event linkage exist. Generic non-song order items, approval/version history, sharing notifications, and conflict resolution do not. |
| Worship planning · Post-service feedback | Completed plan status and song usage relationships | Low | Actual-vs-planned set, ratings, reflections, team feedback, reminders, and historical rating averages have no models or workflows. This must not be implied by the existing usage history. |
| Worship planning · Song recommendations | No current route or model | Excluded | This is explicitly Phase 8. No ranking, suggestion endpoint, recommendation UI, or ML behavior may be built in Phase 7. |
| Song practice initial MOBILE view | Song detail/resource preview, ChordPro preview, choir assignments, rehearsals | Partial | Protected chord/lyric viewing exists. Transpose, tuning, auto-scroll, looping, speed, metronome, and custom playback do not. Spotify remains an official embed, not a custom audio service. |
| Insights · Church reports | No report routes; source records exist across apps | Low | Some aggregates can be derived from existing records, but reports, exports, filters, scheduling, and privacy-aware cross-module queries are Phase 7 work. Volunteer coverage and booking metrics lack source models. |
| Member experience · Member portal | `accounts:dashboard`, `members:my-record`, visible events/registration, own giving | Low partial | Current dashboard is minimal. Upcoming gatherings and service assignments can use existing data; “My bookings,” receipts, and editable contact synchronization are not implemented. |
| Member experience · Notifications | Choir announcements are the only similar feature | None | There is no unified inbox, unread/read state, category filters, preferences, or event/payment/assignment notification model. |
| Member experience · Access and profile settings | `accounts:profile`, password change, administrator user/role forms | Partial | Preferred name, phone, password, account state, and role assignment exist. The role matrix is documentation rather than a current screen. Time zone, digest/booking preferences, church policies, access logs, and multi-church settings do not. |

## Existing implementation comparison

### Reusable without new domain models

- Custom authentication, six roles, and permission-based navigation decisions.
- Member directory, private member detail, self-record, and audit metadata.
- Ministry directory and object-scoped leadership.
- Events, visibility, registration, waitlisting, participant attendance, and
  worship/rehearsal schedule links.
- Confidential funds/contributions and member self-history.
- Choir enrollment, rehearsal schedules/attendance, announcements, and song
  assignments.
- Song metadata, Spotify track ID/embed, protected resources, ChordPro preview,
  usage through plans, setlist ordering, and choir participation.
- The existing CHORD logo assets and Bootstrap 5 dependency.

### Backend work required before full Figma fidelity

- room/resource booking, approval, fees, payment handling, and receipts;
- unified notifications, unread state, delivery preferences, and outbound
  delivery behavior;
- volunteer availability, individual service assignments, coverage, and
  schedule-conflict detection;
- first-time guest attendance and full-roster attendance semantics;
- generic order-of-service items, approval/version history, and team sharing;
- post-service actual usage, reflections, and human ratings;
- global search and any multi-church workspace behavior;
- practice-room transpose/tuning/metronome/looping/custom playback behavior.

These are not frontend-only changes and must not be invented during UI
refinement. They need explicit product scope, permissions, models, migrations,
tests, and security decisions.

## Phase 7 implementation guidance

When Phase 7 is explicitly authorized, the safest sequence is:

1. Establish local design tokens, Lato loading strategy, accessible focus
   states, and the responsive role-aware shell using existing permissions.
2. Replace the minimal dashboard with truthful panels derived only from current
   models. Omit booking, payment, and notification cards until those domains
   exist.
3. Refine existing member, ministry, event, giving, choir, song, resource, and
   worship-plan templates using reusable partials for cards, filters, tables,
   status pills, empty states, and pagination.
4. Add privacy-aware reports only for existing data sources, with explicit
   permission checks and query-efficiency tests.
5. Treat every unsupported Figma area as deferred or separately scoped rather
   than adding dead navigation or static mock data.

## Accessibility and responsive risks

- Much of the desktop UI uses 10-12 px text. Confirm readable minimum sizes,
  zoom behavior, and WCAG contrast before copying values literally.
- The 232 px desktop rail and dense tables have no demonstrated mobile
  variants. A collapsible navigation and responsive table/card strategy is
  required.
- All icon-only controls need accessible names, visible keyboard focus, and
  adequate touch targets.
- Status must remain expressed by text as well as color. The designs generally
  include labels, which should be preserved.
- Loading, no-results, form-error, permission-denied, and destructive-action
  confirmation states are not comprehensively represented.
- The mobile practice controls require keyboard/screen-reader semantics and a
  licensing/product decision before they can be treated as implementable.

## Audit conclusion

The Figma design is a coherent direction for Phase 7's shell, dashboard,
reports, and refinement of implemented modules. It is not a literal Phase 7
specification for every visible feature. The highest-value reusable direction
is the role-aware desktop shell and the consistent card/table/status language.

Phase 7 implementation remains **not started**. Booking/payment, unified
notifications, advanced volunteer scheduling, advanced worship feedback, and
practice-player behavior are documented gaps. Machine learning recommendations
remain **reserved for Phase 8 and not in progress**.

See [[Development-Roadmap]], [[Task-Tracker]], [[Known-Issues]],
[[Development-Log]], and [[../02-Architecture/Architecture-Decisions]].
