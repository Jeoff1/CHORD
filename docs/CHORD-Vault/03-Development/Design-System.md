# CHORD Design System

**Status:** Phase 7.2 foundation implemented on 2026-11-09  
**Source:** [[Phase-7-Figma-Design-Audit]] and the shared Django shell

## Foundation

The primary application experience follows the audited desktop Figma system.
Tokens and shared component refinements live in `static/css/chord.css`. Bootstrap
5 remains the layout and component base; CHORD adds a small project-owned token
layer rather than a new frontend framework.

### Color tokens

| Purpose | Token | Value |
| --- | --- | --- |
| Primary action/navigation | `--chord-color-primary` | `#285744` |
| Strong primary/text | `--chord-color-primary-strong` | `#233a32` |
| Soft primary state | `--chord-color-primary-soft` | `#e9f0e9` |
| Application canvas | `--chord-color-canvas` | `#f6f5f0` |
| Sidebar | `--chord-color-sidebar` | `#eeeee6` |
| Main surface | `--chord-color-surface` | `#ffffff` |
| Subtle surface/header | `--chord-color-surface-subtle` | `#fbfaf7` |
| Muted text | `--chord-color-muted` | `#748078` |
| Borders | `--chord-color-border` | `#dfe4dc` |

Semantic info, warning, danger, and success colors are also defined for status
pills and messages. Status remains visible as text, not color alone.

### Typography

- Primary desktop family: Lato 400/700, loaded from Google Fonts with system
  fallbacks.
- Shared sizes range from 12 px metadata to 24 px headings.
- The audited mobile practice screen's Inter/amber system is intentionally not
  merged into the shared shell. It remains a specialized future experience.

### Spacing, radii, and shadows

- Spacing tokens cover 4, 8, 12, 16, 24, and 32 px increments.
- Controls use an 8 px radius; cards use 12 px; avatars/statuses use pills.
- Cards use a minimal one-pixel shadow. The mobile navigation drawer uses a
  stronger overlay shadow.
- The desktop shell retains the audited 232 px sidebar and 74 px header.

## Shared components

The foundation styles or provides:

- primary, outlined, small, and link-style buttons;
- form controls and Django `form.as_p` widgets;
- cards, list groups, tables, pagination, and alerts;
- semantic status-pill variants;
- CHORD identity, workspace context, and signed-in identity;
- permission-aware navigation and active states;
- application header, breadcrumb, date, and profile shortcut;
- branded unauthenticated/authentication layout;
- skip link, keyboard focus treatment, and reduced-motion behavior.

Reusable template partials live under `templates/includes/`:

- `chord_brand.html`
- `user_avatar.html`
- `application_sidebar.html`
- `application_header.html`

Navigation state is presentation-only and comes from
`apps.accounts.context_processors.application_shell`. Server-side permission
mixins and querysets remain the authorization source of truth.

## Responsive behavior

- At desktop widths, the sidebar is fixed and the application workspace is
  offset by its width.
- Below 992 px, the sidebar becomes an off-canvas drawer with a backdrop,
  explicit close control, Escape handling, focus movement, and body scroll
  locking.
- Below 576 px, breadcrumb and date details collapse while the current section,
  menu action, and profile shortcut remain available.
- Tables retain horizontal overflow until each individual screen receives its
  later Phase 7 refinement.

## Deliberate omissions

The foundation does not add navigation for Bookings, Recommendations, Reports,
or Notifications because those routes do not currently exist. It also does not
invent global search or a multi-church selector. The workspace card is a
non-interactive, truthful single-workspace label.

Exact Figma navigation icons were not available as durable local assets after
the Starter MCP limit. The shell uses accessible text navigation rather than
substitute icons. This can be revisited when the exact assets are available.

See [[Branding-and-Assets]], [[Screen-Implementation-Tracker]],
[[Design-Change-Log]], and [[Known-Issues]].
