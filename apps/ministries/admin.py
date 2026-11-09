from django.contrib import admin

from .models import Ministry, MinistryMembership


class MinistryMembershipInline(admin.TabularInline):
    model = MinistryMembership
    extra = 0
    autocomplete_fields = ("member", "assigned_by")


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("name", "description")
    readonly_fields = ("public_id", "created_at", "updated_at")
    inlines = (MinistryMembershipInline,)


@admin.register(MinistryMembership)
class MinistryMembershipAdmin(admin.ModelAdmin):
    list_display = ("ministry", "member", "role", "status", "joined_on")
    list_filter = ("role", "status", "ministry")
    search_fields = ("ministry__name", "member__first_name", "member__last_name")
    list_select_related = ("ministry", "member", "assigned_by")
    autocomplete_fields = ("ministry", "member", "assigned_by")
    readonly_fields = ("created_at", "updated_at")
