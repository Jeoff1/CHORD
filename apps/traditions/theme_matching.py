"""Match free-string legacy song themes to controlled Themes.

Kept free of model imports so data migrations can use it.
"""


def theme_key(text):
    """Normalize a theme string or code: lowercase, hyphens as spaces, single spaces."""
    return " ".join(str(text).replace("-", " ").lower().split())


def match_legacy_themes(strings, themes):
    """Split legacy strings into (matched Themes, unmatched strings).

    ``themes`` is any iterable of objects with ``code``, ``name`` and
    ``tradition_id``. A common Theme wins over a tradition Theme of the same key.
    """
    index = {}
    for theme in sorted(themes, key=lambda t: t.tradition_id is not None):
        for key in (theme_key(theme.code), theme_key(theme.name)):
            index.setdefault(key, theme)
    matched, unmatched = [], []
    for text in strings:
        theme = index.get(theme_key(text))
        if theme is None:
            if text not in unmatched:
                unmatched.append(text)
        elif theme not in matched:
            matched.append(theme)
    return matched, unmatched
