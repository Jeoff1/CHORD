from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, Role, User, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    fk_name = "user"
    extra = 0


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1


@admin.register(User)
class ChordUserAdmin(UserAdmin):
    inlines = (ProfileInline, UserRoleInline)
    list_display = ("username", "email", "is_active", "is_staff")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tradition")
    list_filter = ("tradition",)
    list_select_related = ("tradition",)
    search_fields = ("name", "code")
    filter_horizontal = ("permissions",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_select_related = ("user", "role", "assigned_by")
    search_fields = ("user__username", "role__name")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "preferred_name", "phone_number")
    search_fields = ("user__username", "preferred_name")
