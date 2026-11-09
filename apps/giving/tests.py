from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.members.models import Member

from .models import Contribution, ContributionAuditEvent, Fund

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


def create_role_user(username, role_code):
    user = User.objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


class ContributionModelTests(TestCase):
    def setUp(self):
        self.fund = Fund.objects.create(name="General")
        self.member = Member.objects.create(first_name="Giving", last_name="Member")

    def test_identified_contribution_requires_member(self):
        contribution = Contribution(
            fund=self.fund,
            amount=Decimal("10.00"),
            method=Contribution.Method.CASH,
        )
        with self.assertRaises(ValidationError) as error:
            contribution.full_clean()
        self.assertIn("member", error.exception.message_dict)

    def test_contribution_date_cannot_be_future(self):
        contribution = Contribution(
            member=self.member,
            fund=self.fund,
            amount=Decimal("10.00"),
            method=Contribution.Method.CASH,
            contributed_on=timezone.localdate() + timedelta(days=1),
        )
        with self.assertRaises(ValidationError) as error:
            contribution.full_clean()
        self.assertIn("contributed_on", error.exception.message_dict)


class GivingPermissionTests(TestCase):
    def setUp(self):
        self.administrator = create_role_user("admin", Role.Code.CHURCH_ADMINISTRATOR)
        self.member_user = create_role_user("member", Role.Code.CHURCH_MEMBER)
        self.member = Member.objects.create(
            user=self.member_user,
            first_name="Church",
            last_name="Member",
            membership_status=Member.Status.MEMBER,
        )
        self.fund = Fund.objects.create(name="Missions")
        self.contribution = Contribution.objects.create(
            member=self.member,
            fund=self.fund,
            amount=Decimal("50.00"),
            method=Contribution.Method.ONLINE,
        )

    def test_member_can_view_only_personal_giving_page(self):
        self.client.force_login(self.member_user)
        own_response = self.client.get(reverse("giving:my-contributions"))
        admin_response = self.client.get(reverse("giving:contribution-list"))
        self.assertContains(own_response, "50.00")
        self.assertEqual(admin_response.status_code, 403)

    def test_member_cannot_edit_contribution(self):
        self.client.force_login(self.member_user)
        response = self.client.get(
            reverse("giving:contribution-edit", args=(self.contribution.public_id,))
        )
        self.assertEqual(response.status_code, 403)

    def test_administrator_can_view_giving_register(self):
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("giving:contribution-list"))
        self.assertContains(response, "Missions")
        self.assertContains(response, "50.00")


class GivingWorkflowTests(TestCase):
    def test_recording_contribution_creates_audit_event(self):
        administrator = create_role_user(
            "administrator", Role.Code.CHURCH_ADMINISTRATOR
        )
        member = Member.objects.create(
            first_name="Recorded",
            last_name="Donor",
            membership_status=Member.Status.MEMBER,
        )
        fund = Fund.objects.create(name="Building")
        self.client.force_login(administrator)
        response = self.client.post(
            reverse("giving:contribution-add"),
            {
                "member": member.pk,
                "anonymous_donor": "",
                "fund": fund.pk,
                "amount": "125.00",
                "contributed_on": timezone.localdate(),
                "method": Contribution.Method.BANK,
                "reference": "BANK-001",
                "notes": "",
            },
        )
        self.assertRedirects(response, reverse("giving:contribution-list"))
        contribution = Contribution.objects.get(reference="BANK-001")
        audit_event = ContributionAuditEvent.objects.get(contribution=contribution)
        self.assertEqual(contribution.recorded_by, administrator)
        self.assertEqual(audit_event.action, ContributionAuditEvent.Action.CREATED)
        self.assertEqual(audit_event.actor, administrator)

    def test_anonymous_contribution_is_not_in_member_history(self):
        member_user = create_role_user("member-user", Role.Code.CHURCH_MEMBER)
        Member.objects.create(
            user=member_user,
            first_name="Private",
            last_name="Viewer",
        )
        fund = Fund.objects.create(name="General")
        Contribution.objects.create(
            anonymous_donor=True,
            fund=fund,
            amount=Decimal("20.00"),
            method=Contribution.Method.CASH,
        )
        self.client.force_login(member_user)
        response = self.client.get(reverse("giving:my-contributions"))
        self.assertNotContains(response, "20.00")

    def test_updating_contribution_creates_field_name_only_audit(self):
        administrator = create_role_user("audit-admin", Role.Code.CHURCH_ADMINISTRATOR)
        member = Member.objects.create(first_name="Audit", last_name="Donor")
        fund = Fund.objects.create(name="Audit fund")
        contribution = Contribution.objects.create(
            member=member,
            fund=fund,
            amount=Decimal("30.00"),
            method=Contribution.Method.CASH,
            recorded_by=administrator,
        )
        self.client.force_login(administrator)
        response = self.client.post(
            reverse("giving:contribution-edit", args=(contribution.public_id,)),
            {
                "member": member.pk,
                "anonymous_donor": "",
                "fund": fund.pk,
                "amount": "35.00",
                "contributed_on": contribution.contributed_on,
                "method": Contribution.Method.CASH,
                "reference": "",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        audit_event = contribution.audit_events.get()
        self.assertEqual(audit_event.action, ContributionAuditEvent.Action.UPDATED)
        self.assertIn("amount", audit_event.fields_changed)
        self.assertNotIn("35.00", audit_event.fields_changed)
