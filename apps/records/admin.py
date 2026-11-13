from django.contrib import admin
from django.db import transaction

from .models import ChurchRecord, ChurchRecordAuditEvent, ChurchRecordType
from .services import record_church_record_event


@admin.register(ChurchRecordType)
class ChurchRecordTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "tradition", "sort_order")
    list_filter = ("tradition",)


@admin.register(ChurchRecord)
class ChurchRecordAdmin(admin.ModelAdmin):
    list_display = ("display_name", "record_type", "date", "officiant")
    list_filter = ("record_type__tradition", "record_type")
    search_fields = ("name", "member__first_name", "member__last_name")
    readonly_fields = ("public_id", "created_at", "updated_at")
    autocomplete_fields = ("member",)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_church_record_event(
            record=obj,
            actor=request.user,
            action=(
                ChurchRecordAuditEvent.Action.UPDATED
                if change
                else ChurchRecordAuditEvent.Action.CREATED
            ),
            fields_changed=form.changed_data,
        )


@admin.register(ChurchRecordAuditEvent)
class ChurchRecordAuditEventAdmin(admin.ModelAdmin):
    list_display = ("record", "action", "actor", "occurred_at")
    list_filter = ("action", "occurred_at")
    readonly_fields = ("record", "actor", "action", "fields_changed", "occurred_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
