from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import Http404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin
from apps.events.models import EventParticipant
from apps.events.services import visible_events_for
from apps.ministries.models import Ministry, MinistryMembership

from .forms import MemberForm
from .models import Member, MemberAuditEvent
from .services import record_member_event


def member_profile_queryset():
    active_memberships = MinistryMembership.objects.filter(
        status=MinistryMembership.Status.ACTIVE,
        ministry__status=Ministry.Status.ACTIVE,
    ).select_related("ministry")
    return (
        Member.objects.select_related("user", "choir_enrollment")
        .prefetch_related(
            Prefetch(
                "ministry_memberships",
                queryset=active_memberships,
                to_attr="active_ministry_memberships",
            ),
            "user__roles",
        )
        .all()
    )


def member_profile_context(member, user):
    can_view_sensitive = member.user_id == user.id or user.has_perm(
        "members.view_sensitive_member_data"
    )
    try:
        choir_enrollment = member.choir_enrollment
    except ObjectDoesNotExist:
        choir_enrollment = None

    recent_attendance = EventParticipant.objects.none()
    if user.has_perm("events.view_eventparticipant"):
        recent_attendance = (
            EventParticipant.objects.filter(
                member=member,
                event__in=visible_events_for(user),
            )
            .exclude(attendance_status=EventParticipant.AttendanceStatus.NOT_RECORDED)
            .select_related("event")
            .order_by("-event__starts_at", "-id")[:5]
        )

    return {
        "can_view_sensitive": can_view_sensitive,
        "can_view_attendance": user.has_perm("events.view_eventparticipant"),
        "recent_attendance": recent_attendance,
        "active_ministry_memberships": member.active_ministry_memberships,
        "choir_enrollment": choir_enrollment,
    }


class MemberListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "members.view_member_directory"
    model = Member
    template_name = "members/member_list.html"
    context_object_name = "members"
    paginate_by = 25

    SEGMENTS = {"all", "active", "new", "inactive"}

    def get_queryset(self):
        active_memberships = MinistryMembership.objects.filter(
            status=MinistryMembership.Status.ACTIVE,
            ministry__status=Ministry.Status.ACTIVE,
        ).select_related("ministry")
        queryset = Member.objects.select_related("choir_enrollment").prefetch_related(
            Prefetch(
                "ministry_memberships",
                queryset=active_memberships,
                to_attr="active_ministry_memberships",
            )
        )
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        ministry = self.request.GET.get("ministry", "").strip()
        segment = self.request.GET.get("segment", "all").strip()
        if segment not in self.SEGMENTS:
            segment = "all"
        self.selected_segment = segment
        if query:
            search_filter = Q(first_name__icontains=query) | Q(
                last_name__icontains=query
            )
            if self.request.user.has_perm("members.view_sensitive_member_data"):
                search_filter |= Q(email__icontains=query) | Q(
                    phone_number__icontains=query
                )
            queryset = queryset.filter(search_filter)
        if status in Member.Status.values:
            queryset = queryset.filter(membership_status=status)
        if ministry.isdigit():
            queryset = queryset.filter(
                ministry_memberships__ministry_id=ministry,
                ministry_memberships__status=MinistryMembership.Status.ACTIVE,
            )
        if segment == "active":
            queryset = queryset.exclude(membership_status=Member.Status.INACTIVE)
        elif segment == "new":
            queryset = queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )
        elif segment == "inactive":
            queryset = queryset.filter(membership_status=Member.Status.INACTIVE)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_since = timezone.now() - timedelta(days=30)
        counts = Member.objects.aggregate(
            all=Count("id"),
            active=Count(
                "id",
                filter=~Q(membership_status=Member.Status.INACTIVE),
            ),
            new=Count("id", filter=Q(created_at__gte=new_since)),
            inactive=Count(
                "id",
                filter=Q(membership_status=Member.Status.INACTIVE),
            ),
        )
        context.update(
            {
                "can_view_sensitive": self.request.user.has_perm(
                    "members.view_sensitive_member_data"
                ),
                "directory_counts": counts,
                "ministries": Ministry.objects.filter(
                    status=Ministry.Status.ACTIVE
                ).order_by("name"),
                "query": self.request.GET.get("q", ""),
                "selected_ministry": self.request.GET.get("ministry", ""),
                "selected_segment": getattr(self, "selected_segment", "all"),
                "selected_status": self.request.GET.get("status", ""),
                "status_choices": Member.Status.choices,
            }
        )
        params = self.request.GET.copy()
        params.pop("page", None)
        context["pagination_query"] = params.urlencode()
        return context


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        return member_profile_queryset()

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
        context.update(member_profile_context(self.object, self.request.user))
        return context


class MyMemberRecordView(MemberDetailView):
    def get_object(self, queryset=None):
        try:
            return self.get_queryset().get(user=self.request.user)
        except Member.DoesNotExist as error:
            raise Http404("No member record is linked to this account.") from error


class MemberManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:list")

    def get_queryset(self):
        return member_profile_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object is not None:
            context.update(member_profile_context(self.object, self.request.user))
        return context


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
