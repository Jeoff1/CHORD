import re

DIRECTIVE_PATTERN = re.compile(r"^\{([^}:]+)(?::\s*(.*))?\}$")
CHORD_PATTERN = re.compile(r"\[([^\]\r\n]{1,24})\]")
ROOT_PATTERN = re.compile(r"([A-G])([#b]?)")
CHORD_TOKEN_PATTERN = re.compile(
    r"([A-G][#b]?)((?:maj|min|dim|aug|sus|add|m|M|[0-9#b+()-])*)(?:/([A-G][#b]?))?"
)

NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NOTE_NAMES = ("C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")

DIRECTIVE_LABELS = {
    "title": "Title",
    "t": "Title",
    "subtitle": "Subtitle",
    "st": "Subtitle",
    "artist": "Artist",
    "key": "Key",
    "capo": "Capo",
    "tempo": "Tempo",
}

SECTION_STARTS = {
    "start_of_chorus": "Chorus",
    "soc": "Chorus",
    "start_of_verse": "Verse",
    "sov": "Verse",
    "start_of_bridge": "Bridge",
    "sob": "Bridge",
}


def note_index(note):
    """Return the semitone index (0-11) of a note or key such as "Bb" or "F#m"."""
    match = ROOT_PATTERN.match((note or "").strip())
    if not match:
        return None
    letter, accidental = match.groups()
    shift = {"#": 1, "b": -1}.get(accidental, 0)
    return (NOTE_INDEX[letter] + shift) % 12


def wrap_semitones(semitones):
    """Normalise an offset to the nearest equivalent in -6..+5."""
    return (semitones + 6) % 12 - 6


def key_offset(from_key, to_key):
    """Semitones from one key to another, or 0 when either is unknown."""
    start, end = note_index(from_key), note_index(to_key)
    if start is None or end is None:
        return 0
    return (end - start) % 12


def _shift_note(note, semitones):
    return NOTE_NAMES[(note_index(note) + semitones) % 12]


def transpose_chord(chord, semitones):
    """Transpose a chord token; tokens that are not chords are returned unchanged."""
    match = CHORD_TOKEN_PATTERN.fullmatch(chord)
    if not semitones % 12 or not match:
        return chord
    root, quality, bass = match.groups()
    result = _shift_note(root, semitones) + quality
    if bass:
        result += "/" + _shift_note(bass, semitones)
    return result


def parse_chordpro(content, semitones=0):
    """Parse a safe display subset of ChordPro without producing HTML.

    Chord tokens and the key directive are transposed by ``semitones``.
    """
    metadata = []
    blocks = []
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        directive = DIRECTIVE_PATTERN.fullmatch(line.strip())
        if directive:
            name = directive.group(1).strip().lower()
            value = (directive.group(2) or "").strip()
            if name == "key" and value:
                value = transpose_chord(value, semitones)
            if name in DIRECTIVE_LABELS and value:
                metadata.append((DIRECTIVE_LABELS[name], value))
            elif name in SECTION_STARTS:
                blocks.append(
                    {"kind": "section", "text": value or SECTION_STARTS[name]}
                )
            elif name in {"comment", "c"} and value:
                blocks.append({"kind": "comment", "text": value})
            elif name.startswith("end_of_") or name in {"eoc", "eov", "eob"}:
                continue
            else:
                blocks.append({"kind": "text", "text": line})
            continue

        matches = list(CHORD_PATTERN.finditer(line))
        if not matches:
            blocks.append({"kind": "text", "text": line})
            continue

        segments = []
        prefix = line[: matches[0].start()]
        if prefix:
            segments.append({"chord": "", "lyric": prefix})
        for index, match in enumerate(matches):
            lyric_start = match.end()
            lyric_end = (
                matches[index + 1].start() if index + 1 < len(matches) else len(line)
            )
            segments.append(
                {
                    "chord": transpose_chord(match.group(1).strip(), semitones),
                    "lyric": line[lyric_start:lyric_end],
                }
            )
        blocks.append({"kind": "chord_line", "segments": segments})
    return {"metadata": metadata, "blocks": blocks}
