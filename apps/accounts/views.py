from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from .dashboard import build_dashboard_context
from .forms import ManagedUserCreationForm, ManagedUserUpdateForm, ProfileForm
from .mixins import AuthenticatedPermissionRequiredMixin

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard_context(self.request.user))
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Your profile was updated.")
        return super().form_valid(form)


class AccountPermissionMixin(AuthenticatedPermissionRequiredMixin):
    permission_required = "accounts.manage_accounts"


class AccountCreatePermissionMixin(AccountPermissionMixin):
    permission_required = (
        "accounts.manage_accounts",
        "accounts.assign_roles",
        "accounts.add_user",
    )


class AccountUpdatePermissionMixin(AccountPermissionMixin):
    permission_required = (
        "accounts.manage_accounts",
        "accounts.assign_roles",
        "accounts.change_user",
        "accounts.deactivate_accounts",
    )


class UserListView(AccountPermissionMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    queryset = User.objects.prefetch_related("roles").order_by("username")


class UserCreateView(AccountCreatePermissionMixin, CreateView):
    form_class = ManagedUserCreationForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "The account was created.")
        return super().form_valid(form)


class UserUpdateView(AccountUpdatePermissionMixin, UpdateView):
    model = User
    form_class = ManagedUserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "The account was updated.")
        return super().form_valid(form)
