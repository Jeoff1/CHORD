"""Tradition-config service: the single interface for asking about the active Tradition."""

from dataclasses import dataclass

from .models import ChurchProfile, Tradition

DEFAULT_TRADITION_CODE = "alliance"

# Gateable modules, keyed by their URL namespace. Core areas (overview,
# accounts, church profile) are never gated.
MODULES = {
    "members": "Members",
    "ministries": "Ministries & volunteers",
    "events": "Calendar & attendance",
    "giving": "Giving records",
    "worship": "Choir, songs & service plans",
    "records": "Church records",
}

# Every term a Tradition may rename; presets supply their own values.
BASE_TERMS = {
    "service": "Service",
}


def role_catalogue():
    """Every role definition (common and preset) CHORD synchronizes."""
    from .roles import role_catalogue as catalogue

    return catalogue()


def roles_in_effect():
    """Roles in effect: the common roles plus the active Tradition's roles."""
    from apps.accounts.models import Role

    return Role.objects.in_effect(get_active_tradition())


def users_with_permission(perm):
    """Active users granted ``perm`` ("app_label.codename") by an in-effect role."""
    from django.contrib.auth import get_user_model

    app_label, codename = perm.split(".", 1)
    granting = roles_in_effect().filter(
        permissions__content_type__app_label=app_label,
        permissions__codename=codename,
    )
    return (
        get_user_model().objects.filter(is_active=True, roles__in=granting).distinct()
    )


def allowed_songbooks(profile=None):
    """Songbooks the active Tradition allows setlists to draw songs from."""
    from apps.worship.models import Songbook

    tradition = (profile or get_church_profile()).tradition
    return Songbook.objects.filter(traditions=tradition)


def available_themes(profile=None):
    """Themes on offer: the common list plus the active Tradition's own Themes."""
    from .models import Theme

    tradition = (profile or get_church_profile()).tradition
    return Theme.objects.available_for(tradition)


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


def terms(profile=None):
    """All terms for the active Tradition, falling back to the base vocabulary."""
    tradition = (profile or get_church_profile()).tradition
    return {**BASE_TERMS, **tradition.terminology}


def term(key, profile=None):
    if key not in BASE_TERMS:
        raise KeyError(key)
    return terms(profile)[key]


def enabled_modules(profile=None):
    """Preset defaults for the active Tradition, with the church's overrides applied."""
    profile = profile or get_church_profile()
    return _apply_overrides(
        set(profile.tradition.default_modules) & MODULES.keys(),
        profile.module_overrides,
    )


def _apply_overrides(enabled, overrides):
    on = {code for code, flag in overrides.items() if flag and code in MODULES}
    off = {code for code, flag in overrides.items() if not flag}
    return (enabled | on) - off


def is_module_enabled(code, profile=None, enabled=None):
    """Core areas (anything outside MODULES) are always enabled."""
    if code not in MODULES:
        return True
    return code in (enabled if enabled is not None else enabled_modules(profile))


def module_overrides_for(tradition, enabled):
    """Overrides that make ``tradition``'s defaults yield exactly ``enabled``."""
    defaults = set(tradition.default_modules)
    return {
        code: code in enabled
        for code in MODULES
        if (code in enabled) != (code in defaults)
    }


def set_module_enabled(code, is_enabled):
    if code not in MODULES:
        raise KeyError(code)
    profile = get_church_profile()
    enabled = _apply_overrides(enabled_modules(profile), {code: is_enabled})
    profile.module_overrides = module_overrides_for(profile.tradition, enabled)
    profile.save(update_fields=["module_overrides", "updated_at"])


class ModuleScopedPerms:
    """A user's permissions, limited to modules enabled for this church.

    Use it to decide what to *show*; views keep their own permission checks.
    A permission's app label is its module code (``"giving.manage_giving"``).
    """

    def __init__(self, user, profile=None):
        self.user = user
        self.enabled = enabled_modules(profile)

    def module_enabled(self, app_label):
        return is_module_enabled(app_label, enabled=self.enabled)

    def has_perm(self, perm):
        return self.module_enabled(perm.split(".", 1)[0]) and self.user.has_perm(perm)

    def has_perms(self, perms):
        return all(self.has_perm(perm) for perm in perms)


def available_service_templates(profile=None):
    """Service Templates the active Tradition offers for new worship plans."""
    from .models import ServiceTemplate

    tradition = (profile or get_church_profile()).tradition
    return ServiceTemplate.objects.filter(tradition=tradition)


def church_calendar(profile=None):
    """The active Tradition's Seasons and Occasions, in date order."""
    from .models import Occasion, Season

    tradition = (profile or get_church_profile()).tradition
    return {
        "seasons": Season.objects.filter(tradition=tradition),
        "occasions": Occasion.objects.filter(tradition=tradition),
    }


def season_for(day, profile=None, seasons=None):
    """The active Tradition's Season containing ``day``, or None (always for INC).

    Pass ``seasons`` (from ``church_calendar``) to resolve many dates in one query.
    """
    if seasons is None:
        seasons = church_calendar(profile)["seasons"]
    return next((s for s in seasons if s.start_date <= day <= s.end_date), None)


@dataclass(frozen=True)
class SlotContext:
    """What a worship plan's Song Slot asks of a song: future Phase 8 input.

    Pure context; nothing here ranks or scores songs.
    """

    service_theme: object  # Theme or None (older plans)
    season: object  # Season or None (always None for INC)
    songbooks: object  # QuerySet of allowed Songbooks
    song_slot: object  # SongSlot


def slot_context(plan, song_slot, profile=None):
    """Service Theme, Season, allowed Songbooks and target slot for one plan slot.

    Raises ValueError if ``song_slot`` is not in the plan's Service Template.
    """
    if song_slot.template_id != plan.service_template_id:
        raise ValueError("Song Slot is not part of this plan's Service Template.")
    profile = profile or get_church_profile()
    return SlotContext(
        service_theme=plan.service_theme,
        season=season_for(plan.service_date, profile),
        songbooks=allowed_songbooks(profile),
        song_slot=song_slot,
    )
