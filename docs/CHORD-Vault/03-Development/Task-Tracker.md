# Task Tracker

## Completed phases

- [x] Phase 1: Environment and Django Foundation
- [x] Phase 2: Authentication and Role-Based Access Control
- [x] Phase 3: Core Church Administration (reported complete; verified by QA)
- [x] Phase 4: Choir and Worship Management
- [x] Phase 5: Remaining Core Modules and System Integration
- [x] Phase 6: Song Resources and Chord Sheet Integration

## Phase 5 completion

- [x] Audit code, vault, permissions, migrations, and requirements
- [x] Add ministry records and member/leader assignments
- [x] Enforce assigned-ministry object permissions for Ministry Leaders
- [x] Add church-wide event calendar, visibility, status, registration,
  capacity/waitlist, and attendance
- [x] Link optional canonical events to worship plans and choir rehearsals
- [x] Synchronize linked schedule and location data
- [x] Add funds, confidential contribution recording, audit metadata, and
  member self-history
- [x] Add PostgreSQL constraints and supporting indexes
- [x] Update all six authoritative role mappings
- [x] Apply migrations and pass the full 94-test suite
- [x] Pass Django checks, migration consistency, Ruff lint, and Ruff format
- [x] Update the Obsidian vault and `AGENTS.md`

## Phase 6 completion

- [x] Normalize supported Spotify track URLs, URIs, and identifiers
- [x] Render Spotify's official track embed with an external-link fallback
- [x] Add protected inline PDF and image responses
- [x] Add escaped UTF-8 text preview and basic safe ChordPro formatting
- [x] Preserve download fallback for Word and unsupported previews
- [x] Add authorized resource update and secure file replacement
- [x] Record the last resource updater and update timestamp
- [x] Add resource access to setlists, assignments, and rehearsal preparation
- [x] Apply `worship.0003` and verify the PostgreSQL schema and permissions
- [x] Pass 107 tests, checks, migration consistency, Ruff, and server smoke
- [x] Update the Obsidian vault and `AGENTS.md`

## Planned phases

- [ ] Phase 7: Dashboard, Reports, and UI/UX Refinement
- [ ] Phase 8: Machine Learning Song Recommendation
- [ ] Phase 9: Final Testing, Security, and Deployment

Phase 8 is reserved and not in progress. Do not implement ML behavior until it
is explicitly authorized. Do not proceed to Phase 7 automatically.

## Phase 7 pre-implementation audit

- [x] Verify read-only authenticated Figma MCP access
- [x] Inventory all 19 top-level Figma screens
- [x] Analyze the desktop and mobile visual systems, logo, shell, navigation,
  components, and layouts
- [x] Map every Figma screen to existing Django modules and routes
- [x] Separate existing capabilities from backend gaps and design-only concepts
- [x] Preserve Recommendations as Phase 8-only scope
- [ ] Implement the Phase 7 dashboard, reports, or UI/UX changes

The audit does not start or complete Phase 7 implementation. See
[[Phase-7-Figma-Design-Audit]].

See [[Development-Roadmap]], [[Known-Issues]], and
[[../04-Testing/Phase-6-Test-Results]].
