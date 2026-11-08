from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login


class AuthenticatedPermissionRequiredMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    """Redirect anonymous users to login and return 403 for denied users."""

    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()
