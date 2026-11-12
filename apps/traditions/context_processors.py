from django.contrib.auth.context_processors import PermLookupDict, PermWrapper

from . import services


class _NoPerms(PermLookupDict):
    def __getitem__(self, perm_name):
        return False

    def __bool__(self):
        return False


class ModuleScopedPermWrapper(PermWrapper):
    """Template ``perms`` that report False for every disabled module.

    Replacing ``perms`` hides each permission-gated link to a disabled module
    across all templates, without per-link checks.
    """

    def __init__(self, user, scoped):
        super().__init__(user)
        self.scoped = scoped

    def __getitem__(self, app_label):
        if not self.scoped.module_enabled(app_label):
            return _NoPerms(self.user, app_label)
        return super().__getitem__(app_label)

    def __contains__(self, perm_name):
        return self.scoped.has_perm(perm_name)


def active_tradition(request):
    """Expose the Church Profile, its terminology and module-scoped perms."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    profile = services.get_church_profile()
    scoped = services.ModuleScopedPerms(request.user, profile)
    return {
        "church_profile": profile,
        "active_tradition": profile.tradition,
        "tradition_terms": services.terms(profile),
        "perms": ModuleScopedPermWrapper(request.user, scoped),
    }
