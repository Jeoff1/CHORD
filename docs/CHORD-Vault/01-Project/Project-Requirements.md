# Project Requirements

## Implemented baseline

- Environment-driven Django/PostgreSQL foundation
- Custom user, profiles, six roles, and server-side RBAC
- Privacy-aware church member administration
- Choir enrollment, rehearsals, attendance, and announcements
- Structured worship song metadata and protected resources
- Worship plans, setlists, participation, assignments, and song usage history

## Phase 5 implemented scope

- Reuse member records for ministry and event participation.
- Model ministries and object-scoped ministry leadership.
- Provide a church-wide event calendar with scheduling, visibility, status,
  capacity, registration, and attendance.
- Allow Ministry Leaders to manage only their assigned ministries and events.
- Connect existing worship plans and rehearsals to canonical event schedules
  without recreating their working records.
- Record confidential contributions by fund with Church Administrator-only
  management and member self-history.
- Preserve exact role boundaries, PostgreSQL constraints, audit metadata, and
  the existing Bootstrap UI conventions.

All items above were implemented and verified on 2026-11-09. Optional event
links preserve existing standalone Phase 4 records; no data migration or record
duplication was required.

## Phase 6 implemented scope

- Normalize supported Spotify track links, URIs, and identifiers and render the
  official Spotify track embed without API credentials or custom playback.
- Preview authorized PDF, UTF-8 text, image, and basic ChordPro resources behind
  the existing resource permission.
- Keep unsupported document formats downloadable without exposing private URLs.
- Allow authorized Worship Leaders and Church Administrators to update or
  replace resources while retaining authorization and updater metadata.
- Surface resources from song details, worship setlists, choir assignments, and
  rehearsal preparation.

## Planned after Phase 6

- Phase 7 owns aggregate reports, dashboards, and broad UI/UX refinement.
- Phase 8 exclusively owns machine learning song recommendations.
- Phase 9 owns final security hardening, deployment, and release verification.

## Phase 8 prohibition

Before explicit Phase 8 authorization, do not implement recommendation
algorithms, TF-IDF, cosine similarity, ranking, training, evaluation,
recommendation endpoints/UI, ML-specific tables, or ML-only packages. Preserve
song title, artist, themes, category, key, tempo, plan associations, and usage
history as ordinary domain data.

See [[../03-Development/Development-Roadmap]] and
[[../02-Architecture/Architecture-Decisions]].
