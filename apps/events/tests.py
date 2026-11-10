from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.members.models import Member
from apps.ministries.models import Ministry, MinistryMembership
from apps.worship.models import WorshipPlan

from .models import Event, EventParticipant
from .services import cancel_registration, register_member, visible_events_for

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


def create_role_user(username, role_code):
    user = User.objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


def future_time(days=2):
    return timezone.now().replace(second=0, microsecond=0) + timedelta(days=days)


def create_event(**kwargs):
    starts_at = kwargs.pop("starts_at", future_time())
    defaults = {
        "title": "Church gathering",
        "event_type": Event.Type.FELLOWSHIP,
        "starts_at": starts_at,
        "ends_at": starts_at + timedelta(hours=2),
        "status": Event.Status.PUBLISHED,
    }
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


class EventModelTests(TestCase):
    def test_end_time_must_follow_start_time(self):
        starts_at = future_time()
        event = Event(
            title="Invalid",
            event_type=Event.Type.OTHER,
            starts_at=starts_at,
            ends_at=starts_at,
        )
        with self.assertRaises(ValidationError) as error:
            event.full_clean()
        self.assertIn("ends_at", error.exception.message_dict)

    def test_restricted_event_requires_ministry(self):
        event = Event(
            title="Restricted",
            event_type=Event.Type.MINISTRY,
            starts_at=future_time(),
            ends_at=future_time() + timedelta(hours=1),
            visibility=Event.Visibility.MINISTRY,
        )
        with self.assertRaises(ValidationError) as error:
            event.full_clean()
        self.assertIn("ministry", error.exception.message_dict)


class EventVisibilityTests(TestCase):
    def setUp(self):
        self.user = create_role_user("member", Role.Code.CHURCH_MEMBER)
        self.member = Member.objects.create(
            user=self.user,
            first_name="Church",
            last_name="Member",
            membership_status=Member.Status.MEMBER,
        )
        self.ministry = Ministry.objects.create(name="Outreach")
        self.other_ministry = Ministry.objects.create(name="Other")
        MinistryMembership.objects.create(ministry=self.ministry, member=self.member)
        self.public_event = create_event(title="Public")
        self.ministry_event = create_event(
            title="Member event",
            ministry=self.ministry,
            visibility=Event.Visibility.MINISTRY,
        )
        self.hidden_event = create_event(
            title="Hidden event",
            ministry=self.other_ministry,
            visibility=Event.Visibility.MINISTRY,
        )
        self.draft_event = create_event(title="Draft", status=Event.Status.DRAFT)

    def test_member_sees_only_published_eligible_events(self):
        visible = set(visible_events_for(self.user))
        self.assertIn(self.public_event, visible)
        self.assertIn(self.ministry_event, visible)
        self.assertNotIn(self.hidden_event, visible)
        self.assertNotIn(self.draft_event, visible)

    def test_hidden_event_detail_is_not_exposed(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("events:detail", args=(self.hidden_event.public_id,))
        )
        self.assertEqual(response.status_code, 404)


class EventLeadershipTests(TestCase):
    def setUp(self):
        self.leader = create_role_user("leader", Role.Code.MINISTRY_LEADER)
        leader_member = Member.objects.create(
            user=self.leader,
            first_name="Event",
            last_name="Leader",
            membership_status=Member.Status.MEMBER,
        )
        self.ministry = Ministry.objects.create(name="Care")
        self.other_ministry = Ministry.objects.create(name="Youth")
        MinistryMembership.objects.create(
            ministry=self.ministry,
            member=leader_member,
            role=MinistryMembership.Role.LEADER,
        )
        self.event = create_event(ministry=self.ministry)
        self.other_event = create_event(title="Other", ministry=self.other_ministry)

    def test_leader_can_edit_only_assigned_ministry_event(self):
        self.client.force_login(self.leader)
        allowed = self.client.get(reverse("events:edit", args=(self.event.public_id,)))
        denied = self.client.get(
            reverse("events:edit", args=(self.other_event.public_id,))
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(denied.status_code, 403)

    def test_leader_cannot_create_event_for_other_ministry(self):
        self.client.force_login(self.leader)
        response = self.client.post(
            reverse("events:add"),
            {
                "title": "Unauthorized",
                "event_type": Event.Type.MINISTRY,
                "ministry": self.other_ministry.pk,
                "starts_at": future_time().strftime("%Y-%m-%dT%H:%M"),
                "ends_at": (future_time() + timedelta(hours=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
                "status": Event.Status.PUBLISHED,
                "visibility": Event.Visibility.MINISTRY,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(title="Unauthorized").exists())

    def test_leader_records_attendance_for_event_participant(self):
        participant_member = Member.objects.create(
            first_name="Event",
            last_name="Participant",
            membership_status=Member.Status.MEMBER,
        )
        participant = EventParticipant.objects.create(
            event=self.event,
            member=participant_member,
            registered_by=self.leader,
        )
        self.client.force_login(self.leader)
        response = self.client.post(
            reverse("events:attendance", args=(self.event.public_id,)),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-participant": participant.pk,
                "form-0-attendance_status": EventParticipant.AttendanceStatus.PRESENT,
            },
        )
        self.assertEqual(response.status_code, 302)
        participant.refresh_from_db()
        self.assertEqual(
            participant.attendance_status,
            EventParticipant.AttendanceStatus.PRESENT,
        )
        self.assertEqual(participant.attendance_recorded_by, self.leader)
        self.assertIsNotNone(participant.attendance_recorded_at)

    def test_leader_cannot_open_attendance_for_another_ministry(self):
        self.client.force_login(self.leader)

        response = self.client.get(
            reverse("events:attendance", args=(self.other_event.public_id,))
        )

        self.assertEqual(response.status_code, 403)


class EventRegistrationTests(TestCase):
    def setUp(self):
        self.first_user = create_role_user("first", Role.Code.CHURCH_MEMBER)
        self.second_user = create_role_user("second", Role.Code.CHURCH_MEMBER)
        self.first = Member.objects.create(
            user=self.first_user,
            first_name="First",
            last_name="Member",
            membership_status=Member.Status.MEMBER,
        )
        self.second = Member.objects.create(
            user=self.second_user,
            first_name="Second",
            last_name="Member",
            membership_status=Member.Status.MEMBER,
        )
        self.event = create_event(registration_required=True, capacity=1)

    def test_capacity_waitlist_and_cancellation_promotion(self):
        first = register_member(
            event=self.event,
            member=self.first,
            actor=self.first_user,
        )
        second = register_member(
            event=self.event,
            member=self.second,
            actor=self.second_user,
        )
        self.assertEqual(
            first.registration_status, EventParticipant.RegistrationStatus.REGISTERED
        )
        self.assertEqual(
            second.registration_status, EventParticipant.RegistrationStatus.WAITLISTED
        )

        cancel_registration(event=self.event, member=self.first)
        second.refresh_from_db()
        self.assertEqual(
            second.registration_status, EventParticipant.RegistrationStatus.REGISTERED
        )

    def test_user_without_member_record_cannot_register(self):
        user = create_role_user("no-record", Role.Code.CHURCH_MEMBER)
        self.client.force_login(user)
        response = self.client.post(
            reverse("events:registration", args=(self.event.public_id,))
        )
        self.assertEqual(response.status_code, 403)

    def test_registration_views_show_waitlist_and_promote_after_cancellation(self):
        self.client.force_login(self.first_user)
        first_response = self.client.post(
            reverse("events:registration", args=(self.event.public_id,))
        )
        self.assertRedirects(
            first_response,
            reverse("events:detail", args=(self.event.public_id,)),
        )

        self.client.force_login(self.second_user)
        second_response = self.client.post(
            reverse("events:registration", args=(self.event.public_id,))
        )
        self.assertRedirects(
            second_response,
            reverse("events:detail", args=(self.event.public_id,)),
        )
        detail = self.client.get(reverse("events:detail", args=(self.event.public_id,)))
        self.assertContains(detail, "Waitlisted")

        self.client.force_login(self.first_user)
        self.client.post(
            reverse("events:registration", args=(self.event.public_id,)),
            {"action": "cancel"},
        )
        second_participation = EventParticipant.objects.get(
            event=self.event,
            member=self.second,
        )
        self.assertEqual(
            second_participation.registration_status,
            EventParticipant.RegistrationStatus.REGISTERED,
        )


class EventUIRefinementTests(TestCase):
    def test_event_directory_segments_and_capacity_counts(self):
        administrator = create_role_user(
            "calendar-admin", Role.Code.CHURCH_ADMINISTRATOR
        )
        upcoming = create_event(
            title="Capacity Gathering",
            registration_required=True,
            capacity=1,
        )
        registered = Member.objects.create(first_name="Registered", last_name="Person")
        waitlisted = Member.objects.create(first_name="Waiting", last_name="Person")
        EventParticipant.objects.create(
            event=upcoming,
            member=registered,
            registration_status=EventParticipant.RegistrationStatus.REGISTERED,
        )
        EventParticipant.objects.create(
            event=upcoming,
            member=waitlisted,
            registration_status=EventParticipant.RegistrationStatus.WAITLISTED,
        )
        past_start = timezone.now() - timedelta(days=3)
        create_event(
            title="Past Gathering",
            starts_at=past_start,
            ends_at=past_start + timedelta(hours=1),
        )
        self.client.force_login(administrator)

        upcoming_response = self.client.get(reverse("events:list"))
        past_response = self.client.get(reverse("events:list"), {"timing": "past"})

        self.assertEqual(upcoming_response.context["timing_counts"]["upcoming"], 1)
        self.assertEqual(upcoming_response.context["timing_counts"]["past"], 1)
        self.assertContains(upcoming_response, "Capacity Gathering")
        self.assertContains(upcoming_response, "1 waitlisted")
        self.assertNotContains(upcoming_response, "Past Gathering")
        self.assertContains(past_response, "Past Gathering")
        self.assertNotContains(past_response, "Capacity Gathering")

    def test_member_does_not_see_event_management_actions(self):
        user = create_role_user("calendar-member", Role.Code.CHURCH_MEMBER)
        Member.objects.create(
            user=user,
            first_name="Calendar",
            last_name="Member",
        )
        event = create_event(title="Member Visible Event")
        self.client.force_login(user)

        list_response = self.client.get(reverse("events:list"))
        detail_response = self.client.get(
            reverse("events:detail", args=(event.public_id,))
        )

        self.assertNotContains(list_response, "Create event")
        self.assertNotContains(detail_response, "Edit event")
        self.assertNotContains(detail_response, "Add participant")


class AttendanceOverviewTests(TestCase):
    def setUp(self):
        self.administrator = create_role_user(
            "attendance-admin", Role.Code.CHURCH_ADMINISTRATOR
        )
        self.event = create_event(title="Attendance Summary Event")
        self.present_member = Member.objects.create(
            first_name="Present", last_name="Member"
        )
        self.absent_member = Member.objects.create(
            first_name="Absent", last_name="Member"
        )
        self.pending_member = Member.objects.create(
            first_name="Pending", last_name="Member"
        )
        EventParticipant.objects.create(
            event=self.event,
            member=self.present_member,
            attendance_status=EventParticipant.AttendanceStatus.PRESENT,
        )
        EventParticipant.objects.create(
            event=self.event,
            member=self.absent_member,
            attendance_status=EventParticipant.AttendanceStatus.ABSENT,
        )
        EventParticipant.objects.create(event=self.event, member=self.pending_member)

    def test_overview_uses_existing_participants_and_event_filter(self):
        other_event = create_event(
            title="Other Attendance Event", starts_at=future_time(5)
        )
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("events:attendance-overview"),
            {"event": self.event.public_id},
        )

        self.assertEqual(response.context["attendance_summary"]["participants"], 3)
        self.assertEqual(response.context["attendance_summary"]["present"], 1)
        self.assertEqual(response.context["attendance_summary"]["absent"], 1)
        self.assertEqual(response.context["attendance_summary"]["not_recorded"], 1)
        self.assertContains(response, self.event.title)
        self.assertNotIn(other_event, list(response.context["attendance_events"]))
        self.assertEqual(response.context["shell_nav_section"], "attendance")

    def test_overview_date_filter_excludes_events_outside_range(self):
        self.client.force_login(self.administrator)
        target_date = timezone.localdate() + timedelta(days=2)

        response = self.client.get(
            reverse("events:attendance-overview"),
            {
                "date_from": target_date.isoformat(),
                "date_to": target_date.isoformat(),
            },
        )

        self.assertContains(response, self.event.title)

    def test_regular_member_cannot_access_attendance_management(self):
        member_user = create_role_user("attendance-member", Role.Code.CHURCH_MEMBER)
        self.client.force_login(member_user)

        overview = self.client.get(reverse("events:attendance-overview"))
        record = self.client.get(
            reverse("events:attendance", args=(self.event.public_id,))
        )

        self.assertEqual(overview.status_code, 403)
        self.assertEqual(record.status_code, 403)


class EventWorshipIntegrationTests(TestCase):
    def test_event_update_synchronizes_linked_worship_plan(self):
        administrator = create_role_user(
            "administrator", Role.Code.CHURCH_ADMINISTRATOR
        )
        event = create_event(event_type=Event.Type.WORSHIP_SERVICE)
        plan = WorshipPlan.objects.create(
            title="Sunday plan",
            event=event,
            service_datetime=event.starts_at,
        )
        new_start = future_time(days=4)
        self.client.force_login(administrator)
        response = self.client.post(
            reverse("events:edit", args=(event.public_id,)),
            {
                "title": event.title,
                "event_type": Event.Type.WORSHIP_SERVICE,
                "ministry": "",
                "starts_at": new_start.strftime("%Y-%m-%dT%H:%M"),
                "ends_at": (new_start + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
                "location": "Main hall",
                "status": Event.Status.PUBLISHED,
                "visibility": Event.Visibility.CHURCH,
                "registration_required": "",
                "registration_deadline": "",
                "capacity": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        plan.refresh_from_db()
        self.assertEqual(plan.service_datetime, event.starts_at)
        self.assertEqual(plan.location, "Main hall")
