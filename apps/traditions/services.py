"""Tradition-config service: the single interface for asking about the active Tradition."""

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
}

# Every term a Tradition may rename; presets supply their own values.
BASE_TERMS = {
    "service": "Service",
}


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
