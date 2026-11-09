from django.contrib import admin

from .models import Contribution, ContributionAuditEvent, Fund


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = (
        "contributed_on",
        "member",
        "anonymous_donor",
        "fund",
        "amount",
        "method",
    )
    list_filter = ("fund", "method", "anonymous_donor", "contributed_on")
    search_fields = ("member__first_name", "member__last_name", "reference")
    autocomplete_fields = ("member", "fund", "recorded_by")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(ContributionAuditEvent)
class ContributionAuditEventAdmin(admin.ModelAdmin):
    list_display = ("contribution", "action", "actor", "occurred_at")
    list_filter = ("action", "occurred_at")
    autocomplete_fields = ("contribution", "actor")
    readonly_fields = (
        "contribution",
        "action",
        "actor",
        "fields_changed",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
