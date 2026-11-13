# 11: ChordPro transposition

**What to build:** ChordPro chord sheets display transposed to the setlist's planned key, and viewers can shift the key up or down while viewing. Non-ChordPro resources are unchanged.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Chord tokens transpose by semitones within the existing safe ChordPro subset
- [x] The default offset is the planned key minus the song's default key
- [x] The viewer can adjust the offset with a query parameter
- [x] Resource security and preview permissions are unchanged
- [x] Tests extend the existing Phase 6 ChordPro tests
