# Song Resources and Chord Sheets

Status: **Completed - Phase 6 (2026-11-09)**

## Spotify integration

- Song forms accept an official HTTPS `open.spotify.com` track link, Spotify
  track URI, or 22-character track ID.
- Values are validated as tracks and stored as the normalized ID only.
- Song details render Spotify's official 152-pixel track iframe and retain a
  normal Spotify link as a fallback.
- Albums, playlists, non-Spotify hosts, HTTP links, malformed ports, and invalid
  identifiers are rejected.
- Playback, preview duration, geographic availability, sign-in, cookies, and
  account restrictions remain controlled by Spotify. CHORD does not proxy or
  bypass playback.

## Protected viewing

- PDF and image previews stream inline from a permission-checked Django view.
- UTF-8 text is rendered through autoescaped templates.
- `.cho`, `.chordpro`, and `.crd` files use a small safe display parser for
  common metadata, section, comment, chord, and lyric syntax. It emits data,
  never uploaded HTML.
- Word files and invalid text encodings receive a clear download fallback.
- Every download and preview requires `view_song_resources`; private files
  remain outside `MEDIA_ROOT` with no public URL.
- Inline binary responses use fixed content types and `nosniff`.

## Resource management and integration

- The existing `SongResource` model, protected storage, 10 MiB limit,
  extension allowlist, authorization reference, and exact-one-source constraint
  remain authoritative.
- Worship Leaders and Church Administrators can update metadata or replace the
  file/source. Replaced files are removed only after the database transaction
  commits.
- `updated_by` and `updated_at` capture the latest application update.
- Resources and Spotify links are available from song details, worship-plan
  setlists, a choir member's assignments, and rehearsal songs.
- Rehearsals reuse existing songs through a simple many-to-many relationship;
  no duplicate song or resource model was introduced.

See [[Choir-Worship-Management]],
[[../02-Architecture/Architecture-Decisions]], and
[[../04-Testing/Phase-6-Test-Results]].
