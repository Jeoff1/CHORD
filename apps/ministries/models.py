import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.members.models import Member


class Ministry(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ministries_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "id")
        indexes = [models.Index(fields=("status", "name"))]
        permissions = (
            ("manage_ministries", "Can manage all ministries"),
            ("manage_assigned_ministries", "Can manage assigned ministries"),
            ("view_ministry_directory", "Can view the ministry directory"),
        )

    def __str__(self):
        return self.name


class MinistryMembership(models.Model):
    class Role(models.TextChoices):
        LEADER = "leader", "Leader"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="ministry_memberships",
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    joined_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ministry_memberships_assigned",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "ministry__name",
            "role",
            "member__last_name",
            "member__first_name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("ministry", "member"),
                name="unique_ministry_member",
            )
        ]
        indexes = [models.Index(fields=("ministry", "status", "role"))]

    def clean(self):
        errors = {}
        if self.joined_on and self.joined_on > timezone.localdate():
            errors["joined_on"] = "Join date cannot be in the future."
        if (
            self.member_id
            and self.status == self.Status.ACTIVE
            and self.member.membership_status == Member.Status.INACTIVE
        ):
            errors["status"] = (
                "An inactive church member cannot have an active ministry membership."
            )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.ministry}: {self.member.full_name} ({self.get_role_display()})"
