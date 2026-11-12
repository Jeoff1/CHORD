from . import services


def active_tradition(request):
    """Expose the Church Profile and active Tradition to every template."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    profile = services.get_church_profile()
    return {"church_profile": profile, "active_tradition": profile.tradition}
