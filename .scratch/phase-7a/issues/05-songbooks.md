# 05: Songbooks and metadata-only songs

**What to build:** Songs belong to a Songbook. Each Tradition allows certain Songbooks, and setlist forms offer only songs from allowed Songbooks. A Songbook can be metadata-only (the INC hymnal, copyrighted Catholic hymnals), and its songs refuse lyric and sheet uploads.

**Blocked by:** 01

**Status:** done

- [x] Songbook model; Song gains a Songbook and a metadata-only flag
- [x] Existing songs migrate to a default Songbook
- [x] Setlist song choices are filtered by allowed Songbooks, server-side
- [x] Metadata-only songs reject lyric and sheet SongResource uploads
- [x] The tradition-config service returns allowed Songbooks and is tested directly
