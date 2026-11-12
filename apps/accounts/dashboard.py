from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event
from apps.events.services import visible_events_for
from apps.giving.models import Contribution
from apps.members.models import Member
from apps.ministries.models import Ministry, MinistryMembership
from apps.traditions.services import ModuleScopedPerms, term
from apps.worship.models import SongAssignment, WorshipPlan


def build_dashboard_context(user):
    """Build a permission-scoped dashboard without exposing restricted records."""
    context = {
        "dashboard_roles": list(user.roles.all()),
        "dashboard_display_name": user.get_full_name() or user.username,
    }
    perms = ModuleScopedPerms(user)
    if user.has_perm("accounts.manage_accounts"):
        context.update(_build_administrator_context(user, perms))
    else:
        context.update(_build_member_context(user, perms))
    return context


def _build_administrator_context(user, perms):
    now = timezone.now()
    today = timezone.localdate()
    metrics = []

    upcoming_events = Event.objects.none()
    if perms.has_perm("events.view_event_calendar"):
        upcoming_events = (
            visible_events_for(user)
            .filter(ends_at__gte=now)
            .exclude(status__in=(Event.Status.COMPLETED, Event.Status.CANCELLED))
        )
        metrics.append(
            {
                "label": "Upcoming events",
                "value": upcoming_events.count(),
                "detail": "Scheduled across the church",
                "url": reverse("events:list"),
            }
        )

    recent_members = Member.objects.none()
    if perms.has_perm("members.view_member_directory"):
        active_members = Member.objects.exclude(
            membership_status=Member.Status.INACTIVE
        )
        metrics.insert(
            0,
            {
                "label": "Active people",
                "value": active_members.count(),
                "detail": "Visitors, attendees, and members",
                "url": reverse("members:list"),
            },
        )
        recent_members = Member.objects.order_by("-created_at", "-id")[:5]

    if perms.has_perm("ministries.view_ministry_directory"):
        metrics.append(
            {
                "label": "Active ministries",
                "value": Ministry.objects.filter(status=Ministry.Status.ACTIVE).count(),
                "detail": "Teams serving the community",
                "url": reverse("ministries:list"),
            }
        )

    upcoming_plans = WorshipPlan.objects.none()
    if perms.has_perm("worship.view_worship_plans"):
        upcoming_plans = WorshipPlan.objects.filter(service_datetime__gte=now).exclude(
            status__in=(WorshipPlan.Status.COMPLETED, WorshipPlan.Status.CANCELLED)
        )
        metrics.append(
            {
                "label": "Services in preparation",
                "value": upcoming_plans.count(),
                "detail": "Draft, preparing, or ready",
                "url": reverse("worship:plan-list"),
            }
        )

    monthly_contributions = None
    if perms.has_perm("giving.manage_giving"):
        monthly_contributions = Contribution.objects.filter(
            contributed_on__gte=today.replace(day=1),
            contributed_on__lte=today,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    quick_actions = []
    if perms.has_perms(("members.manage_members", "members.add_member")):
        quick_actions.append({"label": "Add member", "url": reverse("members:add")})
    if perms.has_perms(("events.manage_ministry_events", "events.add_event")):
        quick_actions.append({"label": "Add event", "url": reverse("events:add")})
    if perms.has_perms(("giving.record_contributions", "giving.add_contribution")):
        quick_actions.append(
            {
                "label": "Record contribution",
                "url": reverse("giving:contribution-add"),
            }
        )
    if perms.has_perms(("worship.manage_worship_plans", "worship.add_worshipplan")):
        quick_actions.append(
            {
                "label": f"Create {term('service')} plan",
                "url": reverse("worship:plan-add"),
            }
        )

    return {
        "dashboard_variant": "administrator",
        "dashboard_metrics": metrics,
        "upcoming_events": upcoming_events[:5],
        "recent_members": recent_members,
        "upcoming_plans": upcoming_plans[:4],
        "monthly_contributions": monthly_contributions,
        "quick_actions": quick_actions,
    }


def _build_member_context(user, perms):
    now = timezone.now()
    upcoming_events = Event.objects.none()
    if perms.has_perm("events.view_event_calendar"):
        upcoming_events = visible_events_for(user).filter(ends_at__gte=now)[:5]

    try:
        member = user.member_record
    except ObjectDoesNotExist:
        member = None

    ministry_memberships = MinistryMembership.objects.none()
    assignments = SongAssignment.objects.none()
    if member and perms.has_perm("ministries.view_ministry_directory"):
        ministry_memberships = MinistryMembership.objects.filter(
            member=member,
            status=MinistryMembership.Status.ACTIVE,
            ministry__status=Ministry.Status.ACTIVE,
        ).select_related("ministry")[:5]
    if member and perms.has_perm("worship.view_worship_plans"):
        assignments = (
            SongAssignment.objects.filter(
                enrollment__member=member,
                plan_song__plan__service_datetime__gte=now,
            )
            .select_related("plan_song__song", "plan_song__plan")
            .order_by("plan_song__plan__service_datetime", "plan_song__position")[:5]
        )

    quick_links = []
    if member:
        quick_links.append(
            {"label": "View my member record", "url": reverse("members:my-record")}
        )
    if perms.has_perm("events.view_event_calendar"):
        quick_links.append(
            {"label": "Browse the calendar", "url": reverse("events:list")}
        )
    if perms.has_perm("giving.view_own_contributions"):
        quick_links.append(
            {"label": "View my giving", "url": reverse("giving:my-contributions")}
        )
    if perms.has_perms(
        ("worship.view_choir_schedule", "worship.view_choir_announcements")
    ):
        quick_links.append(
            {"label": "Open choir activity", "url": reverse("worship:choir-activity")}
        )

    return {
        "dashboard_variant": "member",
        "dashboard_member": member,
        "upcoming_events": upcoming_events,
        "ministry_memberships": ministry_memberships,
        "song_assignments": assignments,
        "quick_links": quick_links,
    }
