from django.contrib import messages
from django.forms import modelform_factory
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from . import services
from .forms import CalendarDatesForm, ChurchProfileForm
from .models import Occasion, Season


class ChurchProfileUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    permission_required = (
        "traditions.manage_church_profile",
        "traditions.change_churchprofile",
    )
    form_class = ChurchProfileForm
    template_name = "traditions/church_profile_form.html"
    success_url = reverse_lazy("traditions:church-profile")

    def get_object(self, queryset=None):
        return services.get_church_profile()

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "The church profile was updated.")
        return super().form_valid(form)


class ChurchCalendarView(AuthenticatedPermissionRequiredMixin, TemplateView):
    permission_required = "traditions.manage_church_profile"
    template_name = "traditions/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(services.church_calendar())
        context["tradition"] = services.get_active_tradition()
        return context


class CalendarDatesUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    template_name = "traditions/calendar_dates_form.html"
    success_url = reverse_lazy("traditions:calendar")

    def get_queryset(self):
        # Only the active Tradition's entries are editable.
        return self.model.objects.filter(tradition=services.get_active_tradition())

    def get_form_class(self):
        return modelform_factory(self.model, form=CalendarDatesForm)

    def form_valid(self, form):
        messages.success(self.request, f"Dates for {self.object} were updated.")
        return super().form_valid(form)


class SeasonUpdateView(CalendarDatesUpdateView):
    model = Season
    permission_required = (
        "traditions.manage_church_profile",
        "traditions.change_season",
    )


class OccasionUpdateView(CalendarDatesUpdateView):
    model = Occasion
    permission_required = (
        "traditions.manage_church_profile",
        "traditions.change_occasion",
    )
