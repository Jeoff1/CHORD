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

CHURCH_ADMIN_PERMISSIONS = {
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
}


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_migrate)
def synchronize_roles(sender, **kwargs):
    roles = {}
    for code, name in Role.Code.choices:
        role, _ = Role.objects.update_or_create(
            code=code,
            defaults={"name": name, "description": ROLE_DESCRIPTIONS[code]},
        )
        roles[code] = role

    permission_query = Permission.objects.none()
    for app_label, codenames in CHURCH_ADMIN_PERMISSIONS.items():
        permission_query = permission_query | Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=codenames,
        )
    roles[Role.Code.CHURCH_ADMINISTRATOR].permissions.set(permission_query)
