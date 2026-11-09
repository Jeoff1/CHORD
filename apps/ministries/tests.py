from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.members.models import Member

from .models import Ministry, MinistryMembership
from .services import can_manage_ministry

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


def create_role_user(username, role_code):
    user = User.objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


class MinistryModelTests(TestCase):
    def test_membership_rejects_future_join_date(self):
        ministry = Ministry.objects.create(name="Care")
        member = Member.objects.create(first_name="A", last_name="Member")
        membership = MinistryMembership(
            ministry=ministry,
            member=member,
            joined_on=timezone.localdate() + timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            membership.full_clean()

    def test_inactive_member_cannot_have_active_membership(self):
        ministry = Ministry.objects.create(name="Care")
        member = Member.objects.create(
            first_name="Inactive",
            last_name="Member",
            membership_status=Member.Status.INACTIVE,
        )
        membership = MinistryMembership(ministry=ministry, member=member)
        with self.assertRaises(ValidationError) as error:
            membership.full_clean()
        self.assertIn("status", error.exception.message_dict)


class MinistryPermissionTests(TestCase):
    def setUp(self):
        self.leader = create_role_user("ministry-leader", Role.Code.MINISTRY_LEADER)
        self.leader_member = Member.objects.create(
            user=self.leader,
            first_name="Ministry",
            last_name="Leader",
            membership_status=Member.Status.MEMBER,
        )
        self.led_ministry = Ministry.objects.create(name="Outreach")
        self.other_ministry = Ministry.objects.create(name="Youth")
        MinistryMembership.objects.create(
            ministry=self.led_ministry,
            member=self.leader_member,
            role=MinistryMembership.Role.LEADER,
        )

    def test_role_permissions_are_synchronized(self):
        self.assertTrue(self.leader.has_perm("ministries.manage_assigned_ministries"))
        self.assertFalse(self.leader.has_perm("ministries.manage_ministries"))

    def test_leader_can_manage_only_assigned_ministry(self):
        self.assertTrue(can_manage_ministry(self.leader, self.led_ministry))
        self.assertFalse(can_manage_ministry(self.leader, self.other_ministry))

        self.client.force_login(self.leader)
        allowed = self.client.get(
            reverse("ministries:edit", args=(self.led_ministry.public_id,))
        )
        denied = self.client.get(
            reverse("ministries:edit", args=(self.other_ministry.public_id,))
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(denied.status_code, 403)

    def test_regular_member_cannot_manage_ministry(self):
        member_user = create_role_user("church-member", Role.Code.CHURCH_MEMBER)
        self.client.force_login(member_user)
        response = self.client.get(
            reverse("ministries:edit", args=(self.led_ministry.public_id,))
        )
        self.assertEqual(response.status_code, 403)


class MinistryWorkflowTests(TestCase):
    def test_administrator_can_create_ministry(self):
        administrator = create_role_user(
            "administrator", Role.Code.CHURCH_ADMINISTRATOR
        )
        self.client.force_login(administrator)
        response = self.client.post(
            reverse("ministries:add"),
            {
                "name": "Hospitality",
                "description": "Welcome ministry",
                "status": Ministry.Status.ACTIVE,
            },
        )
        ministry = Ministry.objects.get(name="Hospitality")
        self.assertRedirects(
            response,
            reverse("ministries:detail", args=(ministry.public_id,)),
        )
        self.assertEqual(ministry.created_by, administrator)

    def test_leader_can_add_member_but_cannot_assign_another_leader(self):
        leader = create_role_user("assigned-leader", Role.Code.MINISTRY_LEADER)
        leader_member = Member.objects.create(
            user=leader,
            first_name="Assigned",
            last_name="Leader",
            membership_status=Member.Status.MEMBER,
        )
        candidate = Member.objects.create(
            first_name="New",
            last_name="Participant",
            membership_status=Member.Status.MEMBER,
        )
        ministry = Ministry.objects.create(name="Welcome")
        MinistryMembership.objects.create(
            ministry=ministry,
            member=leader_member,
            role=MinistryMembership.Role.LEADER,
        )
        self.client.force_login(leader)
        response = self.client.post(
            reverse("ministries:membership-add", args=(ministry.public_id,)),
            {
                "member": candidate.pk,
                "role": MinistryMembership.Role.MEMBER,
                "status": MinistryMembership.Status.ACTIVE,
                "joined_on": timezone.localdate(),
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        membership = MinistryMembership.objects.get(
            ministry=ministry,
            member=candidate,
        )
        self.assertEqual(membership.assigned_by, leader)

        second_candidate = Member.objects.create(
            first_name="Second",
            last_name="Candidate",
        )
        denied = self.client.post(
            reverse("ministries:membership-add", args=(ministry.public_id,)),
            {
                "member": second_candidate.pk,
                "role": MinistryMembership.Role.LEADER,
                "status": MinistryMembership.Status.ACTIVE,
                "joined_on": timezone.localdate(),
                "notes": "",
            },
        )
        self.assertEqual(denied.status_code, 200)
        self.assertFalse(
            MinistryMembership.objects.filter(member=second_candidate).exists()
        )
