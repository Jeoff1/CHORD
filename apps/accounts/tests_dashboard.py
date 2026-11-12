from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event
from apps.giving.models import Contribution, Fund
from apps.members.models import Member
from apps.ministries.models import Ministry, MinistryMembership
from apps.worship.models import (
    ChoirEnrollment,
    PlanChoirParticipation,
    PlanSong,
    Song,
    SongAssignment,
    WorshipPlan,
)

from .models import Role, UserRole

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


class DashboardScreenTests(TestCase):
    def assign_role(self, user, code):
        UserRole.objects.create(user=user, role=Role.objects.get(code=code))

    def create_future_event(self, title, **kwargs):
        starts_at = timezone.now() + timedelta(days=2)
        defaults = {
            "event_type": Event.Type.FELLOWSHIP,
            "starts_at": starts_at,
            "ends_at": starts_at + timedelta(hours=2),
            "status": Event.Status.PUBLISHED,
            "visibility": Event.Visibility.CHURCH,
        }
        defaults.update(kwargs)
        return Event.objects.create(title=title, **defaults)

    def test_administrator_dashboard_uses_real_cross_module_data(self):
        administrator = User.objects.create_user("dashboard-admin", password=PASSWORD)
        self.assign_role(administrator, "church_administrator")
        member = Member.objects.create(
            first_name="Maria",
            last_name="Santos",
            membership_status=Member.Status.MEMBER,
        )
        Ministry.objects.create(name="Community Care")
        event = self.create_future_event("Community supper")
        plan = WorshipPlan.objects.create(
            title="Sunday morning service",
            service_datetime=timezone.now() + timedelta(days=4),
            status=WorshipPlan.Status.PREPARING,
        )
        fund = Fund.objects.create(name="General fund")
        Contribution.objects.create(
            member=member,
            fund=fund,
            amount=Decimal("1250.00"),
            method=Contribution.Method.CASH,
        )
        self.client.force_login(administrator)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard_variant"], "administrator")
        self.assertContains(response, "Community operations")
        self.assertContains(response, member.full_name)
        self.assertContains(response, event.title)
        self.assertContains(response, plan.title)
        self.assertContains(response, "1250.00")
        self.assertContains(response, reverse("giving:contribution-add"))

    def test_member_dashboard_respects_event_visibility_and_shows_assignments(self):
        user = User.objects.create_user(
            "dashboard-member",
            first_name="Sofia",
            last_name="Reyes",
            password=PASSWORD,
        )
        self.assign_role(user, "choir_member")
        member = Member.objects.create(
            user=user,
            first_name="Sofia",
            last_name="Reyes",
            membership_status=Member.Status.MEMBER,
        )
        care_ministry = Ministry.objects.create(name="Care Ministry")
        MinistryMembership.objects.create(
            ministry=care_ministry,
            member=member,
            status=MinistryMembership.Status.ACTIVE,
        )
        private_ministry = Ministry.objects.create(name="Private Ministry")
        public_event = self.create_future_event("Open fellowship")
        hidden_event = self.create_future_event(
            "Leader planning meeting",
            ministry=private_ministry,
            visibility=Event.Visibility.LEADERS,
        )
        enrollment = ChoirEnrollment.objects.create(member=member)
        plan = WorshipPlan.objects.create(
            title="Choir Sunday",
            service_datetime=timezone.now() + timedelta(days=5),
        )
        song = Song.objects.create(
            title="Grace and Hope",
            category=Song.Category.CONTEMPORARY,
        )
        plan_song = PlanSong.objects.create(plan=plan, song=song, position=1)
        PlanChoirParticipation.objects.create(plan=plan, enrollment=enrollment)
        SongAssignment.objects.create(plan_song=plan_song, enrollment=enrollment)
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard_variant"], "member")
        self.assertContains(response, "My community")
        self.assertContains(response, public_event.title)
        self.assertNotContains(response, hidden_event.title)
        self.assertContains(response, care_ministry.name)
        self.assertContains(response, song.title)
        self.assertNotContains(response, "Record contribution")
        self.assertNotContains(response, "This month")

    def test_unlinked_account_gets_truthful_empty_state(self):
        user = User.objects.create_user("unlinked-dashboard", password=PASSWORD)
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "has not been linked to this account yet")
        self.assertNotContains(response, reverse("members:my-record"))
