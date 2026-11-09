import re

DIRECTIVE_PATTERN = re.compile(r"^\{([^}:]+)(?::\s*(.*))?\}$")
CHORD_PATTERN = re.compile(r"\[([^\]\r\n]{1,24})\]")

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


def parse_chordpro(content):
    """Parse a safe display subset of ChordPro without producing HTML."""
    metadata = []
    blocks = []
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        directive = DIRECTIVE_PATTERN.fullmatch(line.strip())
        if directive:
            name = directive.group(1).strip().lower()
            value = (directive.group(2) or "").strip()
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
                    "chord": match.group(1).strip(),
                    "lyric": line[lyric_start:lyric_end],
                }
            )
        blocks.append({"kind": "chord_line", "segments": segments})
    return {"metadata": metadata, "blocks": blocks}
