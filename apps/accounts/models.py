from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models

from apps.validators import phone_validator


class RoleQuerySet(models.QuerySet):
    def in_effect(self, tradition=None):
        """Common roles plus those of ``tradition`` (default: the active one)."""
        if tradition is None:
            from apps.traditions.services import get_active_tradition

            tradition = get_active_tradition()
        return self.filter(
            models.Q(tradition__isnull=True) | models.Q(tradition=tradition)
        )


class Role(models.Model):
    """A responsibility-based role that can grant Django permissions.

    A role with no Tradition is common; a Tradition role grants access only
    while its Tradition is the active one.
    """

    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    tradition = models.ForeignKey(
        "traditions.Tradition",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
        help_text="Leave empty for a role common to every Tradition.",
    )
    permissions = models.ManyToManyField(Permission, blank=True)

    objects = RoleQuerySet.as_manager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        if self.tradition_id:
            return f"{self.name} ({self.tradition})"
        return self.name


class User(AbstractUser):
    """CHORD account with support for multiple responsibility-based roles."""

    roles = models.ManyToManyField(
        Role,
        through="UserRole",
        through_fields=("user", "role"),
        related_name="users",
        blank=True,
    )

    class Meta(AbstractUser.Meta):
        permissions = (
            ("manage_accounts", "Can manage user accounts"),
            ("assign_roles", "Can assign roles to users"),
            ("deactivate_accounts", "Can deactivate user accounts"),
        )


class UserRole(models.Model):
    """Auditable assignment connecting a user to one of their roles."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="user_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="role_assignments_made",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("user__username", "role__name")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "role"),
                name="unique_user_role",
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.role}"


class Profile(models.Model):
    """Small account profile; church membership data belongs in a later app."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    preferred_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        validators=(phone_validator,),
    )

    def __str__(self):
        return f"Profile for {self.user.username}"
