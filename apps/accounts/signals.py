from typing import NamedTuple

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Profile, Role

ROLE_DESCRIPTIONS = {
    Role.Code.CHURCH_ADMINISTRATOR: "Manages CHORD accounts and role assignments.",
    Role.Code.MINISTRY_LEADER: "Coordinates ministry members and activities.",
    Role.Code.WORSHIP_LEADER: "Plans worship services and manages worship songs.",
    Role.Code.CHOIR_LEADER: "Coordinates choir members and rehearsals.",
    Role.Code.CHOIR_MEMBER: "Participates in choir assignments and rehearsals.",
    Role.Code.CHURCH_MEMBER: "Uses permitted member-facing CHORD features.",
}

ROLE_PERMISSIONS = {
    Role.Code.CHURCH_ADMINISTRATOR: {
        "traditions": {
            "change_churchprofile",
            "manage_church_profile",
            "view_churchprofile",
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
    Role.Code.WORSHIP_LEADER: {
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
    Role.Code.CHOIR_LEADER: {
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
    Role.Code.CHOIR_MEMBER: {
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
    Role.Code.MINISTRY_LEADER: {
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
    Role.Code.CHURCH_MEMBER: {
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


class TraditionRole(NamedTuple):
    tradition: str  # Tradition preset code
    name: str
    description: str
    permissions_of: str  # common role whose permission set it reuses


# Roles are synchronized here, not in a data migration, because permissions
# only exist once every app has migrated.
TRADITION_ROLES = {
    "rc_parish_priest": TraditionRole(
        "roman-catholic",
        "Parish Priest",
        "Leads the parish and administers CHORD.",
        Role.Code.CHURCH_ADMINISTRATOR,
    ),
    "rc_music_director": TraditionRole(
        "roman-catholic",
        "Music Director",
        "Plans liturgical music and manages the song library.",
        Role.Code.WORSHIP_LEADER,
    ),
    "alliance_senior_pastor": TraditionRole(
        "alliance",
        "Senior Pastor",
        "Leads the church and administers CHORD.",
        Role.Code.CHURCH_ADMINISTRATOR,
    ),
    "alliance_head_deacon": TraditionRole(
        "alliance",
        "Head Deacon",
        "Coordinates deacons, ministries and their activities.",
        Role.Code.MINISTRY_LEADER,
    ),
    "inc_minister": TraditionRole(
        "iglesia-ni-cristo",
        "Minister",
        "Leads the local congregation and administers CHORD.",
        Role.Code.CHURCH_ADMINISTRATOR,
    ),
    "inc_head_deacon": TraditionRole(
        "iglesia-ni-cristo",
        "Head Deacon",
        "Coordinates deacons, ministries and their activities.",
        Role.Code.MINISTRY_LEADER,
    ),
}


def _permissions_for(app_permissions):
    query = Permission.objects.none()
    for app_label, codenames in app_permissions.items():
        query = query | Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=codenames,
        )
    return query


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_migrate)
def synchronize_roles(sender, **kwargs):
    from apps.traditions.models import Tradition

    for code, name in Role.Code.choices:
        role, _ = Role.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "description": ROLE_DESCRIPTIONS[code],
                "tradition": None,
            },
        )
        role.permissions.set(_permissions_for(ROLE_PERMISSIONS.get(code, {})))

    traditions = {t.code: t for t in Tradition.objects.all()}
    for code, preset in TRADITION_ROLES.items():
        tradition = traditions.get(preset.tradition)
        if tradition is None:
            continue
        role, _ = Role.objects.update_or_create(
            code=code,
            defaults={
                "name": preset.name,
                "description": preset.description,
                "tradition": tradition,
            },
        )
        role.permissions.set(_permissions_for(ROLE_PERMISSIONS[preset.permissions_of]))
