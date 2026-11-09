import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.members.models import Member


class Fund(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class Contribution(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CHECK = "check", "Check"
        BANK = "bank", "Bank transfer"
        ONLINE = "online", "Online"
        OTHER = "other", "Other"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    member = models.ForeignKey(
        Member,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    anonymous_donor = models.BooleanField(default=False)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name="contributions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contributed_on = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=16, choices=Method.choices)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="contributions_recorded",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-contributed_on", "-id")
        indexes = [
            models.Index(fields=("contributed_on", "fund")),
            models.Index(fields=("member", "contributed_on")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="contribution_amount_positive",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(anonymous_donor=True) & Q(member__isnull=True))
                    | (Q(anonymous_donor=False) & Q(member__isnull=False))
                ),
                name="contribution_donor_consistent",
            ),
        ]
        permissions = (
            ("manage_giving", "Can manage contribution records"),
            ("record_contributions", "Can record contributions"),
            ("view_own_contributions", "Can view own contribution history"),
        )

    def clean(self):
        errors = {}
        if self.contributed_on and self.contributed_on > timezone.localdate():
            errors["contributed_on"] = "Contribution date cannot be in the future."
        if self.anonymous_donor and self.member_id:
            errors["member"] = "Anonymous contributions cannot be linked to a member."
        if not self.anonymous_donor and not self.member_id:
            errors["member"] = "Select a member or mark the contribution anonymous."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        donor = "Anonymous" if self.anonymous_donor else self.member.full_name
        return f"{donor} - {self.amount} ({self.fund})"


class ContributionAuditEvent(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"

    contribution = models.ForeignKey(
        Contribution,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="contribution_audit_events",
    )
    action = models.CharField(max_length=16, choices=Action.choices)
    fields_changed = models.JSONField(default=list, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-occurred_at", "-id")

    def __str__(self):
        return f"{self.get_action_display()} - {self.contribution.public_id}"
