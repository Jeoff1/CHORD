from django.contrib import admin

from .models import Event, EventParticipant
from .services import synchronize_linked_schedules


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    autocomplete_fields = ("member", "registered_by", "attendance_recorded_by")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "starts_at", "status", "ministry")
    list_filter = ("event_type", "status", "visibility", "ministry")
    search_fields = ("title", "description", "location")
    autocomplete_fields = ("ministry", "created_by")
    readonly_fields = ("public_id", "created_at", "updated_at")
    inlines = (EventParticipantInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        synchronize_linked_schedules(obj)


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "member",
        "registration_status",
        "attendance_status",
        "updated_at",
    )
    list_filter = ("registration_status", "attendance_status")
    search_fields = ("event__title", "member__first_name", "member__last_name")
    list_select_related = ("event", "member", "registered_by")
    autocomplete_fields = (
        "event",
        "member",
        "registered_by",
        "attendance_recorded_by",
    )
