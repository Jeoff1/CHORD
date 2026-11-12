from django.contrib.auth.backends import ModelBackend


class RolePermissionBackend(ModelBackend):
    """Include permissions granted through active users' CHORD roles."""

    def get_group_permissions(self, user_obj, obj=None):
        permissions = super().get_group_permissions(user_obj, obj)
        if obj is not None or not user_obj.is_active or user_obj.is_anonymous:
            return permissions

        # Cached per user object (one request); a Tradition switch takes
        # effect on the next request's freshly loaded user.
        if not hasattr(user_obj, "_role_perm_cache"):
            role_permissions = user_obj.roles.in_effect().values_list(
                "permissions__content_type__app_label",
                "permissions__codename",
            )
            user_obj._role_perm_cache = {
                f"{app_label}.{codename}"
                for app_label, codename in role_permissions
                if app_label and codename
            }
        return permissions | user_obj._role_perm_cache
