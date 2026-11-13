from django.contrib import admin

from .models import (
    ChurchProfile,
    Occasion,
    Season,
    ServiceTemplate,
    SongSlot,
    Theme,
    Tradition,
)


@admin.register(Tradition)
class TraditionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    readonly_fields = ("code",)


@admin.register(ChurchProfile)
class ChurchProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "tradition", "updated_at")
    readonly_fields = ("updated_at", "updated_by")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tradition")
    list_filter = ("tradition",)
    search_fields = ("name", "code")


class SongSlotInline(admin.TabularInline):
    model = SongSlot
    extra = 0


@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tradition")
    list_filter = ("tradition",)
    inlines = (SongSlotInline,)


@admin.register(Season, Occasion)
class CalendarEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "tradition", "start_date", "end_date")
    list_filter = ("tradition",)
    date_hierarchy = "start_date"
