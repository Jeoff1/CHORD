import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class ChurchRecordType(models.Model):
    """A kind of Church Record (Baptism, Marriage, ...) offered by one Tradition."""

    tradition = models.ForeignKey(
        "traditions.Tradition",
        on_delete=models.CASCADE,
        related_name="church_record_types",
    )
    name = models.CharField(max_length=80)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("tradition", "sort_order", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("tradition", "name"), name="unique_record_type_per_tradition"
            )
        ]

    def __str__(self):
        return self.name


class ChurchRecord(models.Model):
    """A confidential sacramental or pastoral record (baptism, marriage, ...)."""

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    record_type = models.ForeignKey(
        ChurchRecordType, on_delete=models.PROTECT, related_name="records"
    )
    member = models.ForeignKey(
        "members.Member",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="church_records",
    )
    name = models.CharField(
        max_length=200, blank=True, help_text="Used when the person is not a member."
    )
    officiant = models.CharField(max_length=200, blank=True)
    place = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date", "-id")
        indexes = [models.Index(fields=("date",))]
        permissions = (
            ("view_church_records", "Can view confidential church records"),
            ("manage_church_records", "Can manage church records"),
        )

    def clean(self):
        if not self.member_id and not self.name.strip():
            raise ValidationError("Link a member or enter a name.")

    def get_absolute_url(self):
        return reverse("records:detail", args=[self.public_id])

    @property
    def display_name(self):
        return self.member.full_name if self.member_id else self.name

    def __str__(self):
        return f"{self.record_type} — {self.display_name}"


class ChurchRecordAuditEvent(models.Model):
    """Audit trail for Church Record changes; field names only, never values."""

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"

    record = models.ForeignKey(
        ChurchRecord, on_delete=models.PROTECT, related_name="audit_events"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="church_record_audit_events",
    )
    action = models.CharField(max_length=16, choices=Action.choices)
    fields_changed = models.JSONField(default=list, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-occurred_at", "-id")

    def __str__(self):
        return f"{self.get_action_display()} — {self.record.public_id}"
