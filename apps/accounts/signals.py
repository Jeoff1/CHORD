from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Profile, Role


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
    # Synchronized after migrate, not in a data migration, because permissions
    # only exist once every app has migrated. The catalogue is authoritative.
    from apps.traditions.models import Tradition
    from apps.traditions.services import role_catalogue

    traditions = {t.code: t for t in Tradition.objects.all()}
    for definition in role_catalogue():
        tradition = None
        if definition.tradition is not None:
            tradition = traditions.get(definition.tradition)
            if tradition is None:
                continue
        role, _ = Role.objects.update_or_create(
            code=definition.code,
            defaults={
                "name": definition.name,
                "description": definition.description,
                "tradition": tradition,
            },
        )
        role.permissions.set(_permissions_for(definition.permissions))
