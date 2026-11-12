# 11: ChordPro transposition

**What to build:** ChordPro chord sheets display transposed to the setlist's planned key, and viewers can shift the key up or down while viewing. Non-ChordPro resources are unchanged.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Chord tokens transpose by semitones within the existing safe ChordPro subset
- [ ] The default offset is the planned key minus the song's default key
- [ ] The viewer can adjust the offset with a query parameter
- [ ] Resource security and preview permissions are unchanged
- [ ] Tests extend the existing Phase 6 ChordPro tests
