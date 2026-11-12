from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from . import services
from .forms import ChurchProfileForm


class ChurchProfileUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    permission_required = "traditions.manage_church_profile"
    form_class = ChurchProfileForm
    template_name = "traditions/church_profile_form.html"
    success_url = reverse_lazy("traditions:church-profile")

    def get_object(self, queryset=None):
        return services.get_church_profile()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "The church profile was updated.")
        return super().form_valid(form)
