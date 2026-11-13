"""Role catalogue: the common roles and each Tradition preset's roles.

This is data, not branching logic: codes appear only as catalogue keys, and
access is always checked through Django permissions.
"""

from typing import NamedTuple


class TraditionRole(NamedTuple):
    tradition: str  # Tradition preset code
    name: str
    description: str
    permissions_of: str  # common role whose permission set it reuses


COMMON_ROLE_NAMES = {
    "church_administrator": "Church Administrator",
    "ministry_leader": "Ministry Leader",
    "worship_leader": "Worship Leader",
    "choir_leader": "Choir Leader",
    "choir_member": "Choir Member",
    "church_member": "Church Member",
}

ROLE_DESCRIPTIONS = {
    "church_administrator": "Manages CHORD accounts and role assignments.",
    "ministry_leader": "Coordinates ministry members and activities.",
    "worship_leader": "Plans worship services and manages worship songs.",
    "choir_leader": "Coordinates choir members and rehearsals.",
    "choir_member": "Participates in choir assignments and rehearsals.",
    "church_member": "Uses permitted member-facing CHORD features.",
}

ROLE_PERMISSIONS = {
    "church_administrator": {
        "traditions": {
            "change_churchprofile",
            "change_occasion",
            "change_season",
            "manage_church_profile",
            "view_churchprofile",
            "view_occasion",
            "view_season",
            "view_tradition",
        },
        "accounts": {
            "add_user",
            "assign_roles",
            "change_profile",
            "change_user",
            "deactivate_accounts",
            "manage_accounts",
            "view_profile",
            "view_role",
            "view_user",
            "view_userrole",
        },
        "members": {
            "add_member",
            "change_member",
            "manage_members",
            "view_member",
            "view_member_directory",
            "view_sensitive_member_data",
            "view_memberauditevent",
        },
        "ministries": {
            "add_ministry",
            "add_ministrymembership",
            "change_ministry",
            "change_ministrymembership",
            "manage_assigned_ministries",
            "manage_ministries",
            "view_ministry",
            "view_ministry_directory",
            "view_ministrymembership",
        },
        "events": {
            "add_event",
            "add_eventparticipant",
            "change_event",
            "change_eventparticipant",
            "manage_events",
            "manage_ministry_events",
            "record_event_attendance",
            "register_for_events",
            "view_event",
            "view_event_calendar",
            "view_eventparticipant",
        },
        "giving": {
            "add_contribution",
            "add_fund",
            "change_contribution",
            "change_fund",
            "manage_giving",
            "record_contributions",
            "view_contribution",
            "view_contributionauditevent",
            "view_fund",
            "view_own_contributions",
        },
        "records": {
            "add_churchrecord",
            "change_churchrecord",
            "manage_church_records",
            "view_church_records",
            "view_churchrecord",
            "view_churchrecordauditevent",
            "view_churchrecordtype",
        },
        "worship": {
            "add_choirannouncement",
            "add_choirenrollment",
            "add_planchoirparticipation",
            "add_plansong",
            "add_rehearsal",
            "add_rehearsalattendance",
            "add_song",
            "add_songassignment",
            "add_songresource",
            "add_worshipplan",
            "change_choirannouncement",
            "change_choirenrollment",
            "change_plansong",
            "change_rehearsal",
            "change_rehearsalattendance",
            "change_song",
            "change_songresource",
            "change_songassignment",
            "change_worshipplan",
            "delete_planchoirparticipation",
            "delete_plansong",
            "delete_songassignment",
            "manage_choir",
            "manage_choir_announcements",
            "manage_rehearsals",
            "manage_song_assignments",
            "manage_song_library",
            "manage_worship_plans",
            "record_rehearsal_attendance",
            "view_choir_announcements",
            "view_choir_roster",
            "view_choir_schedule",
            "view_choirannouncement",
            "view_choirenrollment",
            "view_planchoirparticipation",
            "view_plansong",
            "view_rehearsal",
            "view_rehearsalattendance",
            "view_song",
            "view_song_library",
            "view_song_resources",
            "view_songassignment",
            "view_songresource",
            "view_worship_plans",
            "view_worshipplan",
        },
    },
    "worship_leader": {
        "ministries": {
            "view_ministry",
            "view_ministry_directory",
        },
        "events": {
            "register_for_events",
            "view_event",
            "view_event_calendar",
        },
        "giving": {"view_own_contributions"},
        "worship": {
            "add_planchoirparticipation",
            "add_plansong",
            "add_song",
            "add_songassignment",
            "add_songresource",
            "add_worshipplan",
            "change_plansong",
            "change_song",
            "change_songresource",
            "change_songassignment",
            "change_worshipplan",
            "delete_planchoirparticipation",
            "delete_plansong",
            "delete_songassignment",
            "manage_song_assignments",
            "manage_song_library",
            "manage_worship_plans",
            "view_choir_roster",
            "view_choir_schedule",
            "view_choirenrollment",
            "view_planchoirparticipation",
            "view_plansong",
            "view_rehearsal",
            "view_song",
            "view_song_library",
            "view_song_resources",
            "view_songassignment",
            "view_songresource",
            "view_worship_plans",
            "view_worshipplan",
        },
    },
    "choir_leader": {
        "ministries": {
            "view_ministry",
            "view_ministry_directory",
        },
        "events": {
            "register_for_events",
            "view_event",
            "view_event_calendar",
        },
        "giving": {"view_own_contributions"},
        "worship": {
            "add_choirannouncement",
            "add_choirenrollment",
            "add_rehearsal",
            "add_rehearsalattendance",
            "add_songassignment",
            "change_choirannouncement",
            "change_choirenrollment",
            "change_rehearsal",
            "change_rehearsalattendance",
            "change_songassignment",
            "delete_songassignment",
            "manage_choir",
            "manage_choir_announcements",
            "manage_rehearsals",
            "manage_song_assignments",
            "record_rehearsal_attendance",
            "view_choir_announcements",
            "view_choir_roster",
            "view_choir_schedule",
            "view_choirannouncement",
            "view_choirenrollment",
            "view_planchoirparticipation",
            "view_plansong",
            "view_rehearsal",
            "view_rehearsalattendance",
            "view_song",
            "view_song_library",
            "view_song_resources",
            "view_songassignment",
            "view_songresource",
            "view_worship_plans",
            "view_worshipplan",
        },
    },
    "choir_member": {
        "ministries": {
            "view_ministry",
            "view_ministry_directory",
        },
        "events": {
            "register_for_events",
            "view_event",
            "view_event_calendar",
        },
        "giving": {"view_own_contributions"},
        "worship": {
            "view_choir_announcements",
            "view_choir_schedule",
            "view_choirannouncement",
            "view_plansong",
            "view_rehearsal",
            "view_song",
            "view_song_library",
            "view_song_resources",
            "view_songassignment",
            "view_songresource",
            "view_worship_plans",
            "view_worshipplan",
        },
    },
    "ministry_leader": {
        "ministries": {
            "add_ministrymembership",
            "change_ministry",
            "change_ministrymembership",
            "manage_assigned_ministries",
            "view_ministry",
            "view_ministry_directory",
            "view_ministrymembership",
        },
        "events": {
            "add_event",
            "add_eventparticipant",
            "change_event",
            "change_eventparticipant",
            "manage_ministry_events",
            "record_event_attendance",
            "register_for_events",
            "view_event",
            "view_event_calendar",
            "view_eventparticipant",
        },
        "giving": {"view_own_contributions"},
    },
    "church_member": {
        "ministries": {
            "view_ministry",
            "view_ministry_directory",
        },
        "events": {
            "register_for_events",
            "view_event",
            "view_event_calendar",
        },
        "giving": {"view_own_contributions"},
    },
}


TRADITION_ROLES = {
    "rc_parish_priest": TraditionRole(
        "roman-catholic",
        "Parish Priest",
        "Leads the parish and administers CHORD.",
        "church_administrator",
    ),
    "rc_music_director": TraditionRole(
        "roman-catholic",
        "Music Director",
        "Plans liturgical music and manages the song library.",
        "worship_leader",
    ),
    "alliance_senior_pastor": TraditionRole(
        "alliance",
        "Senior Pastor",
        "Leads the church and administers CHORD.",
        "church_administrator",
    ),
    "alliance_head_deacon": TraditionRole(
        "alliance",
        "Head Deacon",
        "Coordinates deacons, ministries and their activities.",
        "ministry_leader",
    ),
    "inc_minister": TraditionRole(
        "iglesia-ni-cristo",
        "Minister",
        "Leads the local congregation and administers CHORD.",
        "church_administrator",
    ),
    "inc_head_deacon": TraditionRole(
        "iglesia-ni-cristo",
        "Head Deacon",
        "Coordinates deacons, ministries and their activities.",
        "ministry_leader",
    ),
}


class RoleDefinition(NamedTuple):
    code: str
    name: str
    description: str
    tradition: str | None  # Tradition preset code; None for a common role
    permissions: dict[str, set[str]]  # app label -> permission codenames


def role_catalogue():
    """Every role CHORD defines, common roles first."""
    common = [
        RoleDefinition(
            code, name, ROLE_DESCRIPTIONS[code], None, ROLE_PERMISSIONS[code]
        )
        for code, name in COMMON_ROLE_NAMES.items()
    ]
    presets = [
        RoleDefinition(
            code,
            preset.name,
            preset.description,
            preset.tradition,
            ROLE_PERMISSIONS[preset.permissions_of],
        )
        for code, preset in TRADITION_ROLES.items()
    ]
    return common + presets
