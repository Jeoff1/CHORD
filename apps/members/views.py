from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from .forms import MemberForm
from .models import Member, MemberAuditEvent
from .services import record_member_event


class MemberListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "members.view_member_directory"
    model = Member
    template_name = "members/member_list.html"
    context_object_name = "members"
    paginate_by = 25

    def get_queryset(self):
        queryset = Member.objects.all()
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if query:
            search_filter = Q(first_name__icontains=query) | Q(
                last_name__icontains=query
            )
            if self.request.user.has_perm("members.view_sensitive_member_data"):
                search_filter |= Q(email__icontains=query)
            queryset = queryset.filter(search_filter)
        if status in Member.Status.values:
            queryset = queryset.filter(membership_status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Member.Status.choices
        context["selected_status"] = self.request.GET.get("status", "")
        context["query"] = self.request.GET.get("q", "")
        return context


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_object(self, queryset=None):
        member = super().get_object(queryset)
        owns_record = member.user_id == self.request.user.id
        if not owns_record and not self.request.user.has_perm(
            "members.view_member_directory"
        ):
            raise PermissionDenied
        return member

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_view_sensitive"] = (
            self.object.user_id == self.request.user.id
            or self.request.user.has_perm("members.view_sensitive_member_data")
        )
        return context


class MyMemberRecordView(MemberDetailView):
    def get_object(self, queryset=None):
        try:
            return Member.objects.get(user=self.request.user)
        except Member.DoesNotExist as error:
            raise Http404("No member record is linked to this account.") from error


class MemberManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:list")


class MemberCreateView(MemberManageMixin, CreateView):
    permission_required = (
        "members.manage_members",
        "members.add_member",
        "members.view_sensitive_member_data",
    )

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        record_member_event(
            member=self.object,
            actor=self.request.user,
            action=MemberAuditEvent.Action.CREATED,
            fields_changed=form.changed_data,
        )
        messages.success(self.request, "The member record was created.")
        return response


class MemberUpdateView(MemberManageMixin, UpdateView):
    permission_required = (
        "members.manage_members",
        "members.change_member",
        "members.view_sensitive_member_data",
    )
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    @transaction.atomic
    def form_valid(self, form):
        action = (
            MemberAuditEvent.Action.STATUS_CHANGED
            if "membership_status" in form.changed_data
            else MemberAuditEvent.Action.UPDATED
        )
        response = super().form_valid(form)
        record_member_event(
            member=self.object,
            actor=self.request.user,
            action=action,
            fields_changed=form.changed_data,
        )
        messages.success(self.request, "The member record was updated.")
        return response
