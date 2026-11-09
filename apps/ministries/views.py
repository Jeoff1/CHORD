from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from .forms import MinistryForm, MinistryMembershipForm
from .models import Ministry, MinistryMembership
from .services import can_manage_ministry


class MinistryListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "ministries.view_ministry_directory"
    model = Ministry
    template_name = "ministries/ministry_list.html"
    context_object_name = "ministries"
    paginate_by = 25

    def get_queryset(self):
        queryset = Ministry.objects.annotate(
            active_member_count=Count(
                "memberships",
                filter=Q(memberships__status=MinistryMembership.Status.ACTIVE),
            )
        )
        if not self.request.user.has_perm("ministries.manage_ministries"):
            queryset = queryset.filter(status=Ministry.Status.ACTIVE)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context["query"] = self.request.GET.get("q", "")
        context["pagination_query"] = params.urlencode()
        return context


class MinistryDetailView(AuthenticatedPermissionRequiredMixin, DetailView):
    permission_required = "ministries.view_ministry_directory"
    model = Ministry
    template_name = "ministries/ministry_detail.html"
    context_object_name = "ministry"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        queryset = Ministry.objects.all()
        if not self.request.user.has_perm("ministries.manage_ministries"):
            queryset = queryset.filter(status=Ministry.Status.ACTIVE)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = can_manage_ministry(self.request.user, self.object)
        if context["can_manage"]:
            context["memberships"] = self.object.memberships.select_related(
                "member", "assigned_by"
            )
        return context


class MinistryCreateView(AuthenticatedPermissionRequiredMixin, CreateView):
    permission_required = (
        "ministries.manage_ministries",
        "ministries.add_ministry",
    )
    model = Ministry
    form_class = MinistryForm
    template_name = "ministries/ministry_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The ministry was created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("ministries:detail", args=(self.object.public_id,))


class MinistryUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    permission_required = (
        "ministries.manage_assigned_ministries",
        "ministries.change_ministry",
    )
    model = Ministry
    form_class = MinistryForm
    template_name = "ministries/ministry_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_object(self, queryset=None):
        ministry = super().get_object(queryset)
        if not can_manage_ministry(self.request.user, ministry):
            raise PermissionDenied
        return ministry

    def form_valid(self, form):
        if not self.request.user.has_perm("ministries.manage_ministries"):
            form.instance.status = self.object.status
        messages.success(self.request, "The ministry was updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("ministries:detail", args=(self.object.public_id,))


class MembershipManageMixin(AuthenticatedPermissionRequiredMixin):
    model = MinistryMembership
    form_class = MinistryMembershipForm
    template_name = "ministries/membership_form.html"

    def get_ministry(self):
        if not hasattr(self, "ministry"):
            self.ministry = get_object_or_404(
                Ministry,
                public_id=self.kwargs["public_id"],
            )
            if not can_manage_ministry(self.request.user, self.ministry):
                raise PermissionDenied
        return self.ministry

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(ministry=self.get_ministry(), actor=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ministry"] = self.get_ministry()
        return context

    def get_success_url(self):
        return reverse("ministries:detail", args=(self.get_ministry().public_id,))


class MembershipCreateView(MembershipManageMixin, CreateView):
    permission_required = (
        "ministries.manage_assigned_ministries",
        "ministries.add_ministrymembership",
    )

    def form_valid(self, form):
        messages.success(self.request, "The ministry member was added.")
        return super().form_valid(form)


class MembershipUpdateView(MembershipManageMixin, UpdateView):
    permission_required = (
        "ministries.manage_assigned_ministries",
        "ministries.change_ministrymembership",
    )

    def get_object(self, queryset=None):
        return get_object_or_404(
            MinistryMembership,
            pk=self.kwargs["pk"],
            ministry=self.get_ministry(),
        )

    def form_valid(self, form):
        messages.success(self.request, "The ministry membership was updated.")
        return super().form_valid(form)
