"""Tradition-config service: the single interface for asking about the active Tradition."""

from .models import ChurchProfile, Tradition

DEFAULT_TRADITION_CODE = "alliance"


def list_traditions():
    return list(Tradition.objects.order_by("name"))


def get_church_profile():
    profile = (
        ChurchProfile.objects.select_related("tradition")
        .filter(pk=ChurchProfile.SINGLETON_ID)
        .first()
    )
    if profile is None:
        profile = ChurchProfile(
            tradition=Tradition.objects.get(code=DEFAULT_TRADITION_CODE)
        )
        profile.save()
    return profile


def get_active_tradition():
    return get_church_profile().tradition
