from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_date
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

    def get_queryset(self):
        return Fund.objects.annotate(
            contribution_count=Count("contributions"),
            contribution_total=Sum("contributions__amount"),
        ).order_by("name", "id")


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
        query = self.request.GET.get("q", "").strip()
        fund = self.request.GET.get("fund", "").strip()
        method = self.request.GET.get("method", "").strip()
        date_from = parse_date(self.request.GET.get("date_from", ""))
        date_to = parse_date(self.request.GET.get("date_to", ""))
        if query:
            queryset = queryset.filter(
                Q(member__first_name__icontains=query)
                | Q(member__last_name__icontains=query)
                | Q(reference__icontains=query)
                | Q(fund__name__icontains=query)
            )
        if fund.isdigit():
            queryset = queryset.filter(fund_id=fund)
        if method in Contribution.Method.values:
            queryset = queryset.filter(method=method)
        if date_from:
            queryset = queryset.filter(contributed_on__gte=date_from)
        if date_to:
            queryset = queryset.filter(contributed_on__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["funds"] = Fund.objects.all()
        context["method_choices"] = Contribution.Method.choices
        context["query"] = self.request.GET.get("q", "")
        context["selected_fund"] = self.request.GET.get("fund", "")
        context["selected_method"] = self.request.GET.get("method", "")
        context["date_from"] = parse_date(self.request.GET.get("date_from", ""))
        context["date_to"] = parse_date(self.request.GET.get("date_to", ""))
        context["giving_summary"] = contribution_summary(self.object_list)
        context["fund_summaries"] = fund_summaries(self.object_list)
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
        queryset = contributions_for_member_user(self.request.user)
        fund = self.request.GET.get("fund", "").strip()
        date_from = parse_date(self.request.GET.get("date_from", ""))
        date_to = parse_date(self.request.GET.get("date_to", ""))
        if fund.isdigit():
            queryset = queryset.filter(fund_id=fund)
        if date_from:
            queryset = queryset.filter(contributed_on__gte=date_from)
        if date_to:
            queryset = queryset.filter(contributed_on__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "funds": Fund.objects.filter(
                    contributions__member__user=self.request.user
                ).distinct(),
                "selected_fund": self.request.GET.get("fund", ""),
                "date_from": parse_date(self.request.GET.get("date_from", "")),
                "date_to": parse_date(self.request.GET.get("date_to", "")),
                "giving_summary": contribution_summary(self.object_list),
                "fund_summaries": fund_summaries(self.object_list),
            }
        )
        params = self.request.GET.copy()
        params.pop("page", None)
        context["pagination_query"] = params.urlencode()
        return context


def contribution_summary(queryset):
    summary = queryset.aggregate(
        total=Sum("amount"),
        records=Count("pk"),
        anonymous=Count("pk", filter=Q(anonymous_donor=True)),
    )
    summary["total"] = summary["total"] or Decimal("0.00")
    summary["identified"] = summary["records"] - summary["anonymous"]
    return summary


def fund_summaries(queryset):
    return (
        queryset.values("fund_id", "fund__name")
        .annotate(
            total=Sum("amount"),
            records=Count("pk"),
        )
        .order_by("-total", "fund__name")[:3]
    )
