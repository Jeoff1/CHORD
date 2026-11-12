from django.contrib import admin

from .models import ChurchProfile, Tradition


@admin.register(Tradition)
class TraditionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    readonly_fields = ("code",)


@admin.register(ChurchProfile)
class ChurchProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "tradition", "updated_at")
