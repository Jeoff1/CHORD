from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.events.models import Event, EventParticipant
from apps.ministries.models import Ministry, MinistryMembership
from apps.worship.models import ChoirEnrollment

from .models import Member, MemberAuditEvent

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


class MemberModelTests(TestCase):
    def test_full_name_and_default_status(self):
        member = Member.objects.create(first_name="Sample", last_name="Person")
        self.assertEqual(member.full_name, "Sample Person")
        self.assertEqual(member.membership_status, Member.Status.VISITOR)

    def test_one_account_can_link_to_only_one_member_record(self):
        user = User.objects.create_user("linked-user", password=PASSWORD)
        Member.objects.create(first_name="First", last_name="Record", user=user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Member.objects.create(first_name="Second", last_name="Record", user=user)

    def test_future_dates_are_rejected(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        member = Member(
            first_name="Future",
            last_name="Date",
            date_of_birth=tomorrow,
            joined_on=tomorrow,
        )
        with self.assertRaises(ValidationError) as error:
            member.full_clean()
        self.assertIn("date_of_birth", error.exception.message_dict)
        self.assertIn("joined_on", error.exception.message_dict)

    def test_invalid_phone_number_is_rejected(self):
        member = Member(
            first_name="Invalid",
            last_name="Phone",
            phone_number="not-a-phone",
        )
        with self.assertRaises(ValidationError) as error:
            member.full_clean()
        self.assertIn("phone_number", error.exception.message_dict)


class MemberPermissionTests(TestCase):
    def setUp(self):
        self.administrator = User.objects.create_user("member-admin", password=PASSWORD)
        admin_role = Role.objects.get(code="church_administrator")
        UserRole.objects.create(user=self.administrator, role=admin_role)

    def test_church_administrator_has_scoped_member_permissions(self):
        administrator = User.objects.get(pk=self.administrator.pk)
        self.assertTrue(administrator.has_perm("members.manage_members"))
        self.assertTrue(administrator.has_perm("members.view_member_directory"))
        self.assertTrue(administrator.has_perm("members.view_sensitive_member_data"))
        self.assertFalse(administrator.has_perm("members.delete_member"))

    def test_regular_account_has_no_directory_permission(self):
        user = User.objects.create_user("no-directory", password=PASSWORD)
        self.assertFalse(user.has_perm("members.view_member_directory"))


class MemberDirectoryTests(TestCase):
    def setUp(self):
        self.administrator = User.objects.create_user(
            "directory-admin", password=PASSWORD
        )
        admin_role = Role.objects.get(code="church_administrator")
        UserRole.objects.create(user=self.administrator, role=admin_role)
        self.active_member = Member.objects.create(
            first_name="Alpha",
            last_name="Member",
            email="alpha@example.test",
            membership_status=Member.Status.MEMBER,
        )
        self.visitor = Member.objects.create(
            first_name="Beta",
            last_name="Visitor",
            email="beta@example.test",
            membership_status=Member.Status.VISITOR,
        )

    def test_directory_requires_permission(self):
        user = User.objects.create_user("ordinary", password=PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse("members:list"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_directory_request_redirects_to_login(self):
        response = self.client.get(reverse("members:list"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('members:list')}",
        )

    def test_directory_searches_and_filters(self):
        self.client.force_login(self.administrator)
        response = self.client.get(
            reverse("members:list"),
            {"q": "Alpha", "status": Member.Status.MEMBER},
        )
        self.assertContains(response, self.active_member.full_name)
        self.assertNotContains(response, self.visitor.full_name)

    def test_directory_filters_by_active_ministry_membership(self):
        ministry = Ministry.objects.create(name="Welcome Team")
        MinistryMembership.objects.create(
            ministry=ministry,
            member=self.active_member,
            status=MinistryMembership.Status.ACTIVE,
        )
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("members:list"),
            {"ministry": ministry.pk},
        )

        self.assertContains(response, self.active_member.full_name)
        self.assertContains(response, ministry.name)
        self.assertNotContains(response, self.visitor.full_name)

    def test_directory_segments_report_counts_and_filter_inactive_records(self):
        inactive = Member.objects.create(
            first_name="Archived",
            last_name="Person",
            membership_status=Member.Status.INACTIVE,
        )
        Member.objects.filter(pk=inactive.pk).update(
            created_at=timezone.now() - timedelta(days=60)
        )
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("members:list"),
            {"segment": "inactive"},
        )

        self.assertContains(response, "All members · 3")
        self.assertContains(response, "Active · 2")
        self.assertContains(response, "Inactive · 1")
        self.assertContains(response, inactive.full_name)
        self.assertNotContains(response, self.active_member.full_name)

    def test_directory_renders_prefetched_ministry_and_choir_affiliations(self):
        ministry = Ministry.objects.create(name="Worship Ministry")
        MinistryMembership.objects.create(
            ministry=ministry,
            member=self.active_member,
            status=MinistryMembership.Status.ACTIVE,
        )
        ChoirEnrollment.objects.create(
            member=self.active_member,
            voice_part=ChoirEnrollment.VoicePart.ALTO,
        )
        self.client.force_login(self.administrator)

        response = self.client.get(reverse("members:list"))

        self.assertContains(response, ministry.name)
        self.assertContains(response, "Choir (Alto)")

    def test_directory_renders_pagination_and_preserves_filters(self):
        ministry = Ministry.objects.create(name="Pagination Ministry")
        MinistryMembership.objects.create(
            ministry=ministry,
            member=self.active_member,
            status=MinistryMembership.Status.ACTIVE,
        )
        Member.objects.bulk_create(
            [
                Member(
                    first_name=f"Paged {index}",
                    last_name="Member",
                    membership_status=Member.Status.MEMBER,
                )
                for index in range(25)
            ]
        )
        self.client.force_login(self.administrator)
        response = self.client.get(
            reverse("members:list"),
            {
                "q": "Member",
                "status": Member.Status.MEMBER,
                "segment": "active",
            },
        )
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, "q=Member")
        self.assertContains(response, f"status={Member.Status.MEMBER}")
        self.assertContains(response, "segment=active")

    def test_email_search_requires_sensitive_permission(self):
        viewer = User.objects.create_user("directory-viewer", password=PASSWORD)
        role = Role.objects.get(code="ministry_leader")
        directory_permission = Permission.objects.get(
            content_type__app_label="members",
            codename="view_member_directory",
        )
        role.permissions.add(directory_permission)
        UserRole.objects.create(user=viewer, role=role)
        self.client.force_login(viewer)

        response = self.client.get(reverse("members:list"), {"q": "alpha@example"})
        self.assertNotContains(response, self.active_member.full_name)

    def test_limited_directory_view_does_not_render_contact_columns(self):
        viewer = User.objects.create_user("privacy-viewer", password=PASSWORD)
        role = Role.objects.get(code="ministry_leader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="members",
                codename="view_member_directory",
            )
        )
        UserRole.objects.create(user=viewer, role=role)
        self.active_member.phone_number = "+63 912 345 6789"
        self.active_member.save(update_fields=("phone_number", "updated_at"))
        self.client.force_login(viewer)

        response = self.client.get(reverse("members:list"))

        self.assertContains(response, self.active_member.full_name)
        self.assertNotContains(response, self.active_member.email)
        self.assertNotContains(response, self.active_member.phone_number)
        self.assertNotContains(response, "Contact number")


class MemberAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("record-owner", password=PASSWORD)
        self.member = Member.objects.create(
            user=self.owner,
            first_name="Record",
            last_name="Owner",
            email="private-owner@example.test",
            phone_number="+63 900 000 0000",
        )

    def test_member_can_view_own_sensitive_record(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("members:my-record"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.email)
        self.assertContains(response, self.member.phone_number)

    def test_member_cannot_view_another_record(self):
        other = User.objects.create_user("other-member", password=PASSWORD)
        self.client.force_login(other)
        response = self.client.get(
            reverse("members:detail", args=(self.member.public_id,))
        )
        self.assertEqual(response.status_code, 403)

    def test_directory_only_view_hides_sensitive_fields(self):
        viewer = User.objects.create_user("limited-viewer", password=PASSWORD)
        role = Role.objects.get(code="ministry_leader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="members",
                codename="view_member_directory",
            )
        )
        UserRole.objects.create(user=viewer, role=role)
        self.client.force_login(viewer)

        response = self.client.get(
            reverse("members:detail", args=(self.member.public_id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.full_name)
        self.assertNotContains(response, self.member.email)
        self.assertNotContains(response, self.member.phone_number)

    def test_unlinked_account_gets_not_found_for_own_record(self):
        user = User.objects.create_user("unlinked", password=PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse("members:my-record"))
        self.assertEqual(response.status_code, 404)


class MemberProfileScreenTests(TestCase):
    def setUp(self):
        self.administrator = User.objects.create_user(
            "profile-admin", password=PASSWORD
        )
        UserRole.objects.create(
            user=self.administrator,
            role=Role.objects.get(code="church_administrator"),
        )
        self.member = Member.objects.create(
            first_name="Sofia",
            last_name="Reyes",
            email="sofia@example.test",
            phone_number="+63 917 555 0142",
            membership_status=Member.Status.MEMBER,
            joined_on=timezone.localdate() - timedelta(days=30),
        )
        self.ministry = Ministry.objects.create(name="Welcome Ministry")
        MinistryMembership.objects.create(
            ministry=self.ministry,
            member=self.member,
            status=MinistryMembership.Status.ACTIVE,
        )
        ChoirEnrollment.objects.create(
            member=self.member,
            voice_part=ChoirEnrollment.VoicePart.SOPRANO,
        )
        starts_at = timezone.now() - timedelta(days=7)
        self.event = Event.objects.create(
            title="Sunday worship",
            event_type=Event.Type.WORSHIP_SERVICE,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            status=Event.Status.COMPLETED,
            visibility=Event.Visibility.CHURCH,
        )
        EventParticipant.objects.create(
            event=self.event,
            member=self.member,
            attendance_status=EventParticipant.AttendanceStatus.PRESENT,
        )

    def test_profile_presents_supported_affiliations_and_attendance(self):
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("members:detail", args=(self.member.public_id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Identity &amp; contact")
        self.assertContains(response, self.ministry.name)
        self.assertContains(response, "Choir")
        self.assertContains(response, "Soprano")
        self.assertContains(response, self.event.title)
        self.assertContains(response, "Present")
        self.assertNotContains(response, "Contribution records")

    def test_edit_screen_reuses_profile_context_and_real_form_fields(self):
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("members:edit", args=(self.member.public_id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="member-form"')
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="membership_status"')
        self.assertContains(response, self.ministry.name)
        self.assertContains(response, self.event.title)

    def test_profile_attendance_respects_event_visibility(self):
        viewer = User.objects.create_user("profile-viewer", password=PASSWORD)
        role = Role.objects.get(code="ministry_leader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="members",
                codename="view_member_directory",
            )
        )
        UserRole.objects.create(user=viewer, role=role)
        private_ministry = Ministry.objects.create(name="Private Leadership")
        starts_at = timezone.now() - timedelta(days=2)
        hidden_event = Event.objects.create(
            title="Private leader meeting",
            event_type=Event.Type.MINISTRY,
            ministry=private_ministry,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
            status=Event.Status.COMPLETED,
            visibility=Event.Visibility.LEADERS,
        )
        EventParticipant.objects.create(
            event=hidden_event,
            member=self.member,
            attendance_status=EventParticipant.AttendanceStatus.PRESENT,
        )
        self.client.force_login(viewer)

        response = self.client.get(
            reverse("members:detail", args=(self.member.public_id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, hidden_event.title)
        self.assertNotContains(response, self.member.email)


class MemberManagementTests(TestCase):
    def setUp(self):
        self.administrator = User.objects.create_user(
            "management-admin", password=PASSWORD
        )
        admin_role = Role.objects.get(code="church_administrator")
        UserRole.objects.create(user=self.administrator, role=admin_role)
        self.client.force_login(self.administrator)

    def test_create_member_records_audit_event_without_values(self):
        response = self.client.post(
            reverse("members:add"),
            {
                "first_name": "Created",
                "last_name": "Member",
                "email": "created@example.test",
                "phone_number": "+63 912 345 6789",
                "address": "Private test address",
                "membership_status": Member.Status.MEMBER,
            },
        )
        self.assertRedirects(response, reverse("members:list"))
        member = Member.objects.get(first_name="Created", last_name="Member")
        event = member.audit_events.get()
        self.assertEqual(event.action, MemberAuditEvent.Action.CREATED)
        self.assertEqual(event.actor, self.administrator)
        self.assertIn("email", event.fields_changed)
        self.assertNotIn(member.email, str(event.fields_changed))

    def test_status_update_records_status_change(self):
        member = Member.objects.create(
            first_name="Status",
            last_name="Change",
            membership_status=Member.Status.VISITOR,
        )
        response = self.client.post(
            reverse("members:edit", args=(member.public_id,)),
            {
                "first_name": member.first_name,
                "last_name": member.last_name,
                "email": "",
                "phone_number": "",
                "address": "",
                "membership_status": Member.Status.MEMBER,
            },
        )
        self.assertRedirects(response, reverse("members:list"))
        event = member.audit_events.get()
        self.assertEqual(event.action, MemberAuditEvent.Action.STATUS_CHANGED)
        self.assertEqual(event.fields_changed, ["membership_status"])

    def test_create_requires_add_and_sensitive_permissions(self):
        admin_role = Role.objects.get(code="church_administrator")
        admin_role.permissions.remove(
            Permission.objects.get(
                content_type__app_label="members",
                codename="add_member",
            )
        )
        self.administrator = User.objects.get(pk=self.administrator.pk)
        self.client.force_login(self.administrator)

        response = self.client.get(reverse("members:add"))

        self.assertEqual(response.status_code, 403)

    def test_update_requires_change_and_sensitive_permissions(self):
        member = Member.objects.create(first_name="Protected", last_name="Member")
        admin_role = Role.objects.get(code="church_administrator")
        admin_role.permissions.remove(
            Permission.objects.get(
                content_type__app_label="members",
                codename="change_member",
            )
        )
        self.administrator = User.objects.get(pk=self.administrator.pk)
        self.client.force_login(self.administrator)

        response = self.client.get(reverse("members:edit", args=(member.public_id,)))

        self.assertEqual(response.status_code, 403)
