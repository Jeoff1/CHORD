import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError

SPOTIFY_TRACK_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{22}$")


def validate_spotify_track_id(value):
    if value and not SPOTIFY_TRACK_ID_PATTERN.fullmatch(value):
        raise ValidationError("Enter a valid 22-character Spotify track ID.")


def normalize_spotify_track(value):
    """Return a track ID from a supported Spotify URL, URI, or raw identifier."""
    candidate = (value or "").strip()
    if not candidate:
        return ""

    if candidate.startswith("spotify:"):
        parts = candidate.split(":")
        if len(parts) != 3 or parts[:2] != ["spotify", "track"]:
            raise ValidationError("Only Spotify track URIs are supported.")
        track_id = parts[2]
    elif "://" in candidate:
        parsed = urlsplit(candidate)
        try:
            port = parsed.port
        except ValueError as error:
            raise ValidationError("Use a valid Spotify track link.") from error
        if (
            parsed.scheme != "https"
            or parsed.hostname != "open.spotify.com"
            or port is not None
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValidationError("Use an official HTTPS open.spotify.com track link.")
        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) == 2 and segments[0] == "track":
            track_id = segments[1]
        elif len(segments) == 3 and segments[:2] == ["embed", "track"]:
            track_id = segments[2]
        elif (
            len(segments) == 3
            and segments[0].startswith("intl-")
            and segments[1] == "track"
        ):
            track_id = segments[2]
        else:
            raise ValidationError("Only Spotify track links are supported.")
    else:
        track_id = candidate

    validate_spotify_track_id(track_id)
    return track_id
