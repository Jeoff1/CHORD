"""Tradition-config service: the single interface for asking about the active Tradition."""

from .models import ChurchProfile, Tradition

DEFAULT_TRADITION_CODE = "alliance"


def list_traditions():
    return list(Tradition.objects.all())


def get_church_profile():
    """Return the Church Profile; a data migration creates it, this only self-heals."""
    profile, _ = ChurchProfile.objects.select_related("tradition").get_or_create(
        pk=ChurchProfile.SINGLETON_ID,
        defaults={"tradition": Tradition.objects.get(code=DEFAULT_TRADITION_CODE)},
    )
    return profile


def get_active_tradition():
    return get_church_profile().tradition
