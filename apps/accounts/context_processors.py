SECTION_LABELS = {
    "overview": "Overview",
    "accounts": "Account administration",
    "profile": "Access & profile",
    "members": "Members",
    "attendance": "Attendance",
    "ministries": "Ministries & volunteers",
    "events": "Calendar",
    "giving": "Giving records",
    "choir": "Choir",
    "songs": "Song library",
    "plans": "Service plans",
}


def application_shell(request):
    """Expose presentation-only navigation state to the shared shell."""
    match = request.resolver_match
    if match is None:
        return {
            "shell_nav_section": "",
            "shell_section_label": "Church workspace",
        }

    app_name = match.app_name or ""
    url_name = match.url_name or ""

    if app_name == "accounts":
        if url_name == "dashboard":
            section = "overview"
        elif url_name.startswith("user-"):
            section = "accounts"
        else:
            section = "profile"
    elif app_name == "events" and url_name in {"attendance", "attendance-overview"}:
        section = "attendance"
    elif app_name == "worship":
        if url_name == "song-assignments" or url_name.startswith("plan-"):
            section = "plans"
        elif url_name.startswith(("song-", "song-resource-")):
            section = "songs"
        else:
            section = "choir"
    else:
        section = {
            "members": "members",
            "ministries": "ministries",
            "events": "events",
            "giving": "giving",
        }.get(app_name, "")

    return {
        "shell_nav_section": section,
        "shell_section_label": SECTION_LABELS.get(section, "Church workspace"),
    }
