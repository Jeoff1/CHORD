import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from apps.members.models import Member
from apps.validators import validate_resource_file_size

from .spotify import validate_spotify_track_id
from .storage import protected_resource_storage


class ChoirEnrollment(models.Model):
    """A member's participation in the church choir, separate from RBAC roles."""

    class VoicePart(models.TextChoices):
        SOPRANO = "soprano", "Soprano"
        ALTO = "alto", "Alto"
        TENOR = "tenor", "Tenor"
        BASS = "bass", "Bass"
        OTHER = "other", "Other / Unassigned"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On leave"
        INACTIVE = "inactive", "Inactive"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    member = models.OneToOneField(
        Member,
        on_delete=models.PROTECT,
        related_name="choir_enrollment",
    )
    voice_part = models.CharField(
        max_length=16,
        choices=VoicePart.choices,
        default=VoicePart.OTHER,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    joined_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("member__last_name", "member__first_name")
        indexes = [models.Index(fields=("status", "voice_part"))]
        permissions = (
            ("manage_choir", "Can manage choir enrollment"),
            ("view_choir_roster", "Can view the choir roster"),
        )

    def clean(self):
        if self.joined_on and self.joined_on > timezone.localdate():
            raise ValidationError({"joined_on": "Join date cannot be in the future."})
        if (
            self.status == self.Status.ACTIVE
            and self.member.membership_status == Member.Status.INACTIVE
        ):
            raise ValidationError(
                {
                    "status": "An inactive church member cannot have an active choir enrollment."
                }
            )

    def __str__(self):
        return f"{self.member.full_name} ({self.get_voice_part_display()})"


class Rehearsal(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.OneToOneField(
        "events.Event",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="rehearsal",
    )
    title = models.CharField(max_length=150)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    songs = models.ManyToManyField(
        "Song",
        blank=True,
        related_name="rehearsals",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="rehearsals_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("starts_at", "id")
        indexes = [models.Index(fields=("status", "starts_at"))]
        permissions = (
            ("manage_rehearsals", "Can manage choir rehearsals"),
            ("view_choir_schedule", "Can view the choir schedule"),
            ("record_rehearsal_attendance", "Can record rehearsal attendance"),
        )

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after the start time."})

    def __str__(self):
        return f"{self.title} - {timezone.localtime(self.starts_at):%Y-%m-%d}"


class RehearsalAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        LATE = "late", "Late"
        ABSENT = "absent", "Absent"
        EXCUSED = "excused", "Excused"

    rehearsal = models.ForeignKey(
        Rehearsal,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    enrollment = models.ForeignKey(
        ChoirEnrollment,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    notes = models.CharField(max_length=250, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="rehearsal_attendance_recorded",
    )
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("enrollment__member__last_name", "enrollment__member__first_name")
        constraints = [
            models.UniqueConstraint(
                fields=("rehearsal", "enrollment"),
                name="unique_rehearsal_enrollment_attendance",
            )
        ]

    def __str__(self):
        return f"{self.rehearsal}: {self.enrollment} - {self.get_status_display()}"


class ChoirAnnouncement(models.Model):
    class Audience(models.TextChoices):
        ALL = "all", "All choir participants"
        LEADERS = "leaders", "Choir leaders"
        MEMBERS = "members", "Choir members"

    title = models.CharField(max_length=150)
    body = models.TextField()
    audience = models.CharField(
        max_length=16,
        choices=Audience.choices,
        default=Audience.ALL,
    )
    published_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="choir_announcements_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-id")
        indexes = [models.Index(fields=("published_at", "expires_at"))]
        permissions = (
            ("manage_choir_announcements", "Can manage choir announcements"),
            ("view_choir_announcements", "Can view choir announcements"),
        )

    def clean(self):
        if self.expires_at and self.expires_at <= self.published_at:
            raise ValidationError(
                {"expires_at": "Expiry must be after the publication time."}
            )

    def __str__(self):
        return self.title


class Songbook(models.Model):
    """A hymnal or song library a Song belongs to (see GLOSSARY.md)."""

    DEFAULT_CODE = "general"

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=150, unique=True)
    metadata_only = models.BooleanField(
        default=False,
        help_text="Store titles and metadata only; refuse lyric and sheet resources.",
    )
    traditions = models.ManyToManyField(
        "traditions.Tradition",
        blank=True,
        related_name="songbooks",
        help_text="Traditions whose setlists may use this songbook.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


def default_songbook_id():
    songbook, _ = Songbook.objects.get_or_create(
        code=Songbook.DEFAULT_CODE, defaults={"name": "General Library"}
    )
    return songbook.pk


class Song(models.Model):
    class Category(models.TextChoices):
        CONTEMPORARY = "contemporary", "Contemporary worship"
        GOSPEL = "gospel", "Gospel"
        HYMN = "hymn", "Hymn"
        SPECIAL = "special", "Special music"
        OTHER = "other", "Other"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200, blank=True)
    default_key = models.CharField(max_length=8, blank=True)
    tempo_bpm = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(MinValueValidator(20), MaxValueValidator(300)),
    )
    category = models.CharField(max_length=24, choices=Category.choices)
    themes = models.ManyToManyField(
        "traditions.Theme", blank=True, related_name="songs"
    )
    legacy_themes = models.JSONField(
        default=list,
        blank=True,
        help_text="Free-string themes no controlled Theme matched; tag them by hand.",
    )
    songbook = models.ForeignKey(
        Songbook,
        on_delete=models.PROTECT,
        default=default_songbook_id,
        related_name="songs",
    )
    metadata_only = models.BooleanField(
        default=False,
        help_text="Store metadata only; refuse lyric and sheet resources.",
    )
    notes = models.TextField(blank=True)
    spotify_track_id = models.CharField(
        max_length=22,
        blank=True,
        validators=(validate_spotify_track_id,),
        help_text="Normalized Spotify track identifier used by the official embed.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="songs_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title", "artist", "id")
        indexes = [
            models.Index(fields=("title", "artist")),
            models.Index(fields=("category",)),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(tempo_bpm__isnull=True)
                    | (models.Q(tempo_bpm__gte=20) & models.Q(tempo_bpm__lte=300))
                ),
                name="song_tempo_valid_range",
            )
        ]
        permissions = (
            ("manage_song_library", "Can manage the worship song library"),
            ("view_song_library", "Can view the worship song library"),
            ("view_song_resources", "Can view authorized song resources"),
        )

    @property
    def is_metadata_only(self):
        return self.metadata_only or self.songbook.metadata_only

    @property
    def theme_text(self):
        return ", ".join(theme.name for theme in self.themes.all())

    @property
    def spotify_url(self):
        if not self.spotify_track_id:
            return ""
        return f"https://open.spotify.com/track/{self.spotify_track_id}"

    @property
    def spotify_embed_url(self):
        if not self.spotify_track_id:
            return ""
        return f"https://open.spotify.com/embed/track/{self.spotify_track_id}"

    def __str__(self):
        return f"{self.title} - {self.artist}" if self.artist else self.title


class SongResource(models.Model):
    class ResourceType(models.TextChoices):
        CHORD_SHEET = "chord_sheet", "Chord sheet"
        LEAD_SHEET = "lead_sheet", "Lead sheet"
        LYRICS = "lyrics", "Lyrics"
        REFERENCE_AUDIO = "reference_audio", "Reference audio"
        OTHER = "other", "Other"

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=150)
    resource_type = models.CharField(max_length=24, choices=ResourceType.choices)
    file = models.FileField(
        upload_to="worship/song-resources/%Y/%m/",
        blank=True,
        storage=protected_resource_storage,
        validators=(
            FileExtensionValidator(
                allowed_extensions=(
                    "pdf",
                    "doc",
                    "docx",
                    "txt",
                    "cho",
                    "chordpro",
                    "crd",
                    "png",
                    "jpg",
                    "jpeg",
                )
            ),
            validate_resource_file_size,
        ),
    )
    external_url = models.URLField(blank=True)
    authorization_reference = models.CharField(
        max_length=250,
        help_text="Record the license, permission, or source authorizing this resource.",
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="song_resources_added",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="song_resources_updated",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("resource_type", "title", "id")
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(file="") & ~models.Q(external_url=""))
                    | (~models.Q(file="") & models.Q(external_url=""))
                ),
                name="song_resource_exactly_one_source",
            )
        ]

    LYRIC_AND_SHEET_TYPES = frozenset(
        {ResourceType.CHORD_SHEET, ResourceType.LEAD_SHEET, ResourceType.LYRICS}
    )

    def clean(self):
        if bool(self.file) == bool(self.external_url):
            raise ValidationError(
                "Provide either one uploaded file or one external URL."
            )
        if (
            self.song_id
            and self.resource_type in self.LYRIC_AND_SHEET_TYPES
            and self.song.is_metadata_only
        ):
            raise ValidationError(
                {
                    "resource_type": "This song is metadata only; lyrics and "
                    "sheets cannot be stored."
                }
            )

    @property
    def file_extension(self):
        if not self.file:
            return ""
        return (
            self.file.name.rsplit(".", 1)[-1].lower() if "." in self.file.name else ""
        )

    @property
    def preview_kind(self):
        if self.file_extension == "pdf":
            return "pdf"
        if self.file_extension in {"txt"}:
            return "text"
        if self.file_extension in {"cho", "chordpro", "crd"}:
            return "chordpro"
        if self.file_extension in {"png", "jpg", "jpeg"}:
            return "image"
        return ""

    @property
    def is_previewable(self):
        return bool(self.preview_kind)

    def __str__(self):
        return f"{self.song}: {self.title}"


class WorshipPlan(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.OneToOneField(
        "events.Event",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="worship_plan",
    )
    title = models.CharField(max_length=200)
    service_datetime = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    preparation_notes = models.TextField(blank=True)
    # Required for new plans (enforced by WorshipPlanForm); null for older plans.
    service_theme = models.ForeignKey(
        "traditions.Theme",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="worship_plans",
    )
    sermon_title = models.CharField(max_length=200, blank=True)
    scripture_reference = models.CharField(max_length=120, blank=True)
    songs = models.ManyToManyField(
        Song, through="PlanSong", related_name="worship_plans"
    )
    choir_participants = models.ManyToManyField(
        ChoirEnrollment,
        through="PlanChoirParticipation",
        related_name="worship_plans",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="worship_plans_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-service_datetime", "-id")
        indexes = [models.Index(fields=("status", "service_datetime"))]
        permissions = (
            ("manage_worship_plans", "Can manage worship service plans"),
            ("view_worship_plans", "Can view worship service plans"),
        )

    def __str__(self):
        return f"{self.title} - {timezone.localtime(self.service_datetime):%Y-%m-%d}"


class PlanSong(models.Model):
    plan = models.ForeignKey(
        WorshipPlan,
        on_delete=models.CASCADE,
        related_name="setlist_items",
    )
    song = models.ForeignKey(Song, on_delete=models.PROTECT, related_name="plan_items")
    position = models.PositiveSmallIntegerField()
    planned_key = models.CharField(max_length=8, blank=True)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("plan", "position"),
                name="unique_plan_song_position",
            ),
            models.UniqueConstraint(
                fields=("plan", "song"),
                name="unique_song_per_worship_plan",
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1),
                name="plan_song_position_positive",
            ),
        ]

    def __str__(self):
        return f"{self.plan}: {self.position}. {self.song}"


class PlanChoirParticipation(models.Model):
    plan = models.ForeignKey(
        WorshipPlan,
        on_delete=models.CASCADE,
        related_name="choir_participations",
    )
    enrollment = models.ForeignKey(
        ChoirEnrollment,
        on_delete=models.PROTECT,
        related_name="plan_participations",
    )
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ("enrollment__member__last_name", "enrollment__member__first_name")
        constraints = [
            models.UniqueConstraint(
                fields=("plan", "enrollment"),
                name="unique_plan_choir_participation",
            )
        ]

    def __str__(self):
        return f"{self.plan}: {self.enrollment}"


class SongAssignment(models.Model):
    plan_song = models.ForeignKey(
        PlanSong,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    enrollment = models.ForeignKey(
        ChoirEnrollment,
        on_delete=models.PROTECT,
        related_name="song_assignments",
    )
    notes = models.CharField(max_length=250, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="choir_song_assignments_made",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("plan_song__position", "enrollment__member__last_name")
        constraints = [
            models.UniqueConstraint(
                fields=("plan_song", "enrollment"),
                name="unique_plan_song_enrollment_assignment",
            )
        ]
        permissions = (
            ("manage_song_assignments", "Can manage choir song assignments"),
        )

    def clean(self):
        if self.plan_song_id and self.enrollment_id:
            participates = PlanChoirParticipation.objects.filter(
                plan_id=self.plan_song.plan_id,
                enrollment_id=self.enrollment_id,
            ).exists()
            if not participates:
                raise ValidationError(
                    {
                        "enrollment": "The choir member must participate in this worship plan."
                    }
                )

    def __str__(self):
        return f"{self.plan_song.song}: {self.enrollment}"
