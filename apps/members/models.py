import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.validators import phone_validator


class Member(models.Model):
    """A church member record, optionally linked to a CHORD login account."""

    class Status(models.TextChoices):
        VISITOR = "visitor", "Visitor"
        REGULAR_ATTENDEE = "regular_attendee", "Regular Attendee"
        MEMBER = "member", "Member"
        INACTIVE = "inactive", "Inactive"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="member_record",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        validators=(phone_validator,),
    )
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    membership_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.VISITOR,
    )
    joined_on = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("last_name", "first_name", "id")
        indexes = [
            models.Index(fields=("last_name", "first_name")),
            models.Index(fields=("membership_status",)),
        ]
        permissions = (
            ("manage_members", "Can manage member records"),
            ("view_member_directory", "Can view the member directory"),
            ("view_sensitive_member_data", "Can view sensitive member data"),
        )

    def clean(self):
        today = timezone.localdate()
        errors = {}
        if self.date_of_birth and self.date_of_birth > today:
            errors["date_of_birth"] = "Date of birth cannot be in the future."
        if self.joined_on and self.joined_on > today:
            errors["joined_on"] = "Join date cannot be in the future."
        if errors:
            raise ValidationError(errors)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


class MemberAuditEvent(models.Model):
    """Minimal audit trail for member-record changes."""

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="member_audit_events",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    fields_changed = models.JSONField(default=list, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-occurred_at", "-id")

    def __str__(self):
        return f"{self.get_action_display()} — {self.member}"
