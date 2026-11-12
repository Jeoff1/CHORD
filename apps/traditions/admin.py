from django.contrib import admin

from .models import ChurchProfile, Tradition


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
