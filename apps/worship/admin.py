from django.contrib import admin

from .models import (
    ChoirAnnouncement,
    ChoirEnrollment,
    PlanChoirParticipation,
    PlanSong,
    Rehearsal,
    RehearsalAttendance,
    Song,
    SongAssignment,
    SongResource,
    WorshipPlan,
)
from .services import save_song_resource


@admin.register(ChoirEnrollment)
class ChoirEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("member", "voice_part", "status", "joined_on")
    list_filter = ("status", "voice_part")
    search_fields = ("member__first_name", "member__last_name")
    autocomplete_fields = ("member",)
    readonly_fields = ("public_id", "created_at", "updated_at")


class RehearsalAttendanceInline(admin.TabularInline):
    model = RehearsalAttendance
    extra = 0
    autocomplete_fields = ("enrollment",)


@admin.register(Rehearsal)
class RehearsalAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "location", "status")
    list_filter = ("status",)
    search_fields = ("title", "location")
    readonly_fields = ("public_id", "created_at", "updated_at")
    autocomplete_fields = ("event",)
    inlines = (RehearsalAttendanceInline,)


@admin.register(RehearsalAttendance)
class RehearsalAttendanceAdmin(admin.ModelAdmin):
    list_display = ("rehearsal", "enrollment", "status", "recorded_at")
    list_filter = ("status",)
    list_select_related = ("rehearsal", "enrollment__member", "recorded_by")
    autocomplete_fields = ("rehearsal", "enrollment", "recorded_by")


@admin.register(ChoirAnnouncement)
class ChoirAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "published_at", "expires_at")
    list_filter = ("audience",)
    search_fields = ("title", "body")
    autocomplete_fields = ("created_by",)
    readonly_fields = ("created_at", "updated_at")


class SongResourceInline(admin.TabularInline):
    model = SongResource
    extra = 0
    can_delete = False
    fields = (
        "title",
        "resource_type",
        "authorization_reference",
        "added_by",
        "updated_by",
        "updated_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "category", "default_key", "tempo_bpm")
    list_filter = ("category",)
    search_fields = ("title", "artist")
    readonly_fields = ("public_id", "created_at", "updated_at")
    inlines = (SongResourceInline,)


@admin.register(SongResource)
class SongResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "song",
        "resource_type",
        "added_by",
        "updated_by",
        "updated_at",
    )
    list_filter = ("resource_type",)
    search_fields = ("title", "song__title", "authorization_reference")
    autocomplete_fields = ("song", "added_by", "updated_by")
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        save_song_resource(form=form, song=obj.song, actor=request.user)


class PlanSongInline(admin.TabularInline):
    model = PlanSong
    extra = 0
    autocomplete_fields = ("song",)


class PlanChoirParticipationInline(admin.TabularInline):
    model = PlanChoirParticipation
    extra = 0
    autocomplete_fields = ("enrollment",)


@admin.register(WorshipPlan)
class WorshipPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "service_datetime", "status", "location")
    list_filter = ("status",)
    search_fields = ("title", "location")
    readonly_fields = ("public_id", "created_at", "updated_at")
    autocomplete_fields = ("event",)
    inlines = (PlanSongInline, PlanChoirParticipationInline)


@admin.register(PlanSong)
class PlanSongAdmin(admin.ModelAdmin):
    list_display = ("plan", "position", "song", "planned_key")
    list_select_related = ("plan", "song")
    search_fields = ("plan__title", "song__title", "song__artist")
    autocomplete_fields = ("plan", "song")


@admin.register(PlanChoirParticipation)
class PlanChoirParticipationAdmin(admin.ModelAdmin):
    list_display = ("plan", "enrollment", "notes")
    list_select_related = ("plan", "enrollment__member")
    autocomplete_fields = ("plan", "enrollment")


@admin.register(SongAssignment)
class SongAssignmentAdmin(admin.ModelAdmin):
    list_display = ("plan_song", "enrollment", "assigned_by", "assigned_at")
    list_select_related = (
        "plan_song__plan",
        "plan_song__song",
        "enrollment__member",
        "assigned_by",
    )
    autocomplete_fields = ("plan_song", "enrollment", "assigned_by")
