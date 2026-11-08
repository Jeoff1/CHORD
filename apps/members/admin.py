from django.contrib import admin

from .models import Member, MemberAuditEvent
from .services import record_member_event


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "membership_status", "email", "updated_at")
    list_filter = ("membership_status",)
    search_fields = ("first_name", "last_name", "email")
    readonly_fields = ("public_id", "created_at", "updated_at")
    autocomplete_fields = ("user",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            action = MemberAuditEvent.Action.CREATED
        elif "membership_status" in form.changed_data:
            action = MemberAuditEvent.Action.STATUS_CHANGED
        else:
            action = MemberAuditEvent.Action.UPDATED
        record_member_event(
            member=obj,
            actor=request.user,
            action=action,
            fields_changed=form.changed_data,
        )


@admin.register(MemberAuditEvent)
class MemberAuditEventAdmin(admin.ModelAdmin):
    list_display = ("member", "action", "actor", "occurred_at")
    list_filter = ("action", "occurred_at")
    search_fields = ("member__first_name", "member__last_name", "actor__username")
    readonly_fields = (
        "member",
        "actor",
        "action",
        "fields_changed",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
