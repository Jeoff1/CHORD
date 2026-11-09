from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from .forms import ContributionForm, FundForm
from .models import Contribution, Fund
from .services import (
    contributions_for_member_user,
    record_contribution,
    update_contribution,
)


class FundListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "giving.manage_giving"
    model = Fund
    template_name = "giving/fund_list.html"
    context_object_name = "funds"


class FundManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Fund
    form_class = FundForm
    template_name = "giving/fund_form.html"
    success_url = reverse_lazy("giving:fund-list")


class FundCreateView(FundManageMixin, CreateView):
    permission_required = ("giving.manage_giving", "giving.add_fund")

    def form_valid(self, form):
        messages.success(self.request, "The giving fund was created.")
        return super().form_valid(form)


class FundUpdateView(FundManageMixin, UpdateView):
    permission_required = ("giving.manage_giving", "giving.change_fund")

    def form_valid(self, form):
        messages.success(self.request, "The giving fund was updated.")
        return super().form_valid(form)


class ContributionListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "giving.manage_giving"
    model = Contribution
    template_name = "giving/contribution_list.html"
    context_object_name = "contributions"
    paginate_by = 25

    def get_queryset(self):
        queryset = Contribution.objects.select_related("member", "fund", "recorded_by")
        fund = self.request.GET.get("fund", "").strip()
        method = self.request.GET.get("method", "").strip()
        if fund.isdigit():
            queryset = queryset.filter(fund_id=fund)
        if method in Contribution.Method.values:
            queryset = queryset.filter(method=method)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["funds"] = Fund.objects.all()
        context["method_choices"] = Contribution.Method.choices
        context["selected_fund"] = self.request.GET.get("fund", "")
        context["selected_method"] = self.request.GET.get("method", "")
        params = self.request.GET.copy()
        params.pop("page", None)
        context["pagination_query"] = params.urlencode()
        return context


class ContributionCreateView(AuthenticatedPermissionRequiredMixin, CreateView):
    permission_required = ("giving.record_contributions", "giving.add_contribution")
    model = Contribution
    form_class = ContributionForm
    template_name = "giving/contribution_form.html"

    def form_valid(self, form):
        self.object = record_contribution(form=form, actor=self.request.user)
        messages.success(self.request, "The contribution was recorded.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("giving:contribution-list")


class ContributionUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    permission_required = ("giving.manage_giving", "giving.change_contribution")
    model = Contribution
    form_class = ContributionForm
    template_name = "giving/contribution_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def form_valid(self, form):
        self.object = update_contribution(form=form, actor=self.request.user)
        messages.success(self.request, "The contribution was updated.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("giving:contribution-list")


class MyContributionListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "giving.view_own_contributions"
    template_name = "giving/my_contributions.html"
    context_object_name = "contributions"
    paginate_by = 25

    def get_queryset(self):
        return contributions_for_member_user(self.request.user)
