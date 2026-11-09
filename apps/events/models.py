import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.members.models import Member
from apps.ministries.models import Ministry, MinistryMembership


class Event(models.Model):
    class Type(models.TextChoices):
        WORSHIP_SERVICE = "worship_service", "Worship service"
        REHEARSAL = "rehearsal", "Rehearsal"
        MINISTRY = "ministry", "Ministry activity"
        FELLOWSHIP = "fellowship", "Fellowship"
        OUTREACH = "outreach", "Outreach"
        TRAINING = "training", "Training"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Visibility(models.TextChoices):
        CHURCH = "church", "All church users"
        MINISTRY = "ministry", "Ministry members"
        LEADERS = "leaders", "Ministry leaders"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=24, choices=Type.choices)
    ministry = models.ForeignKey(
        Ministry,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="events",
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    visibility = models.CharField(
        max_length=16,
        choices=Visibility.choices,
        default=Visibility.CHURCH,
    )
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=(MinValueValidator(1),),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("starts_at", "id")
        indexes = [
            models.Index(fields=("status", "starts_at")),
            models.Index(fields=("ministry", "starts_at")),
        ]
        permissions = (
            ("manage_events", "Can manage all church events"),
            ("manage_ministry_events", "Can manage assigned ministry events"),
            ("view_event_calendar", "Can view the church event calendar"),
            ("record_event_attendance", "Can record event attendance"),
            ("register_for_events", "Can register for eligible events"),
        )

    def clean(self):
        errors = {}
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "End time must be after the start time."
        if self.registration_deadline and self.starts_at:
            if self.registration_deadline > self.starts_at:
                errors["registration_deadline"] = (
                    "Registration deadline cannot be after the event starts."
                )
        if self.visibility != self.Visibility.CHURCH and not self.ministry_id:
            errors["ministry"] = "Restricted events must belong to a ministry."
        if self.pk:
            try:
                self.worship_plan
            except ObjectDoesNotExist:
                pass
            else:
                if self.event_type != self.Type.WORSHIP_SERVICE:
                    errors["event_type"] = (
                        "An event linked to a worship plan must remain a worship service."
                    )
            try:
                self.rehearsal
            except ObjectDoesNotExist:
                pass
            else:
                if self.event_type != self.Type.REHEARSAL:
                    errors["event_type"] = (
                        "An event linked to a rehearsal must remain a rehearsal."
                    )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} - {timezone.localtime(self.starts_at):%Y-%m-%d}"


class EventParticipant(models.Model):
    class RegistrationStatus(models.TextChoices):
        REGISTERED = "registered", "Registered"
        WAITLISTED = "waitlisted", "Waitlisted"
        CANCELLED = "cancelled", "Cancelled"

    class AttendanceStatus(models.TextChoices):
        NOT_RECORDED = "not_recorded", "Not recorded"
        PRESENT = "present", "Present"
        LATE = "late", "Late"
        ABSENT = "absent", "Absent"
        EXCUSED = "excused", "Excused"

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="participants",
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="event_participations",
    )
    registration_status = models.CharField(
        max_length=16,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.REGISTERED,
    )
    attendance_status = models.CharField(
        max_length=16,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.NOT_RECORDED,
    )
    notes = models.CharField(max_length=250, blank=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="event_registrations_recorded",
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attendance_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="event_attendance_recorded",
    )
    attendance_recorded_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("member__last_name", "member__first_name", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("event", "member"),
                name="unique_event_member_participation",
            )
        ]
        indexes = [
            models.Index(fields=("event", "registration_status")),
            models.Index(fields=("event", "attendance_status")),
        ]

    def clean(self):
        if not self.event_id or not self.member_id:
            return
        if self.event.visibility == Event.Visibility.CHURCH:
            return

        membership_query = MinistryMembership.objects.filter(
            ministry=self.event.ministry,
            member=self.member,
            status=MinistryMembership.Status.ACTIVE,
        )
        if self.event.visibility == Event.Visibility.LEADERS:
            membership_query = membership_query.filter(
                role=MinistryMembership.Role.LEADER
            )
        if not membership_query.exists():
            raise ValidationError(
                {"member": "This member is not eligible for this event."}
            )

    def __str__(self):
        return f"{self.event}: {self.member.full_name}"
