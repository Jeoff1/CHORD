from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.events.models import Event
from apps.members.models import Member
from apps.traditions.models import Theme

from .models import (
    ChoirAnnouncement,
    ChoirEnrollment,
    PlanChoirParticipation,
    PlanSong,
    Rehearsal,
    RehearsalAttendance,
    Song,
    SongAssignment,
    SongResource,
    WorshipPlan,
)
from .services import move_plan_song, sync_plan_participants

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


def create_role_user(username, role_code):
    user = User.objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


def future_datetime(days=1):
    return timezone.now().replace(second=0, microsecond=0) + timedelta(days=days)


class WorshipModelTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            first_name="Choir",
            last_name="Member",
            membership_status=Member.Status.MEMBER,
        )

    def test_choir_enrollment_rejects_future_join_date(self):
        enrollment = ChoirEnrollment(
            member=self.member,
            joined_on=timezone.localdate() + timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            enrollment.full_clean()

    def test_inactive_member_cannot_have_active_choir_enrollment(self):
        self.member.membership_status = Member.Status.INACTIVE
        self.member.save(update_fields=("membership_status",))
        enrollment = ChoirEnrollment(member=self.member)
        with self.assertRaises(ValidationError) as error:
            enrollment.full_clean()
        self.assertIn("status", error.exception.message_dict)

    def test_rehearsal_requires_end_after_start(self):
        start = future_datetime()
        rehearsal = Rehearsal(title="Invalid", starts_at=start, ends_at=start)
        with self.assertRaises(ValidationError) as error:
            rehearsal.full_clean()
        self.assertIn("ends_at", error.exception.message_dict)

    def test_song_tempo_validation(self):
        song = Song(title="Metadata", category=Song.Category.HYMN, tempo_bpm=301)
        with self.assertRaises(ValidationError):
            song.full_clean()

    def test_resource_requires_exactly_one_source(self):
        song = Song.objects.create(title="Licensed", category=Song.Category.HYMN)
        resource = SongResource(
            song=song,
            title="Missing source",
            resource_type=SongResource.ResourceType.CHORD_SHEET,
            authorization_reference="Test license",
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()

    def test_setlist_constraints_prevent_duplicate_song_and_position(self):
        song = Song.objects.create(title="Unique", category=Song.Category.HYMN)
        plan = WorshipPlan.objects.create(
            title="Plan",
            service_datetime=future_datetime(),
        )
        PlanSong.objects.create(plan=plan, song=song, position=1)
        other_song = Song.objects.create(title="Other", category=Song.Category.GOSPEL)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PlanSong.objects.create(plan=plan, song=other_song, position=1)


class PhaseFourRolePermissionTests(TestCase):
    def test_worship_leader_has_planning_but_not_choir_management(self):
        user = create_role_user("worship-leader", "worship_leader")
        self.assertTrue(user.has_perm("worship.manage_song_library"))
        self.assertTrue(user.has_perm("worship.manage_worship_plans"))
        self.assertFalse(user.has_perm("worship.manage_choir"))

    def test_choir_leader_can_manage_choir_but_not_song_library(self):
        user = create_role_user("choir-leader", "choir_leader")
        self.assertTrue(user.has_perm("worship.manage_choir"))
        self.assertTrue(user.has_perm("worship.record_rehearsal_attendance"))
        self.assertTrue(user.has_perm("worship.view_song_library"))
        self.assertFalse(user.has_perm("worship.manage_song_library"))

    def test_choir_member_has_participant_views_only(self):
        user = create_role_user("choir-participant", "choir_member")
        self.assertTrue(user.has_perm("worship.view_choir_schedule"))
        self.assertTrue(user.has_perm("worship.view_song_resources"))
        self.assertFalse(user.has_perm("worship.view_choir_roster"))
        self.assertFalse(user.has_perm("worship.manage_song_assignments"))


class ChoirWorkflowTests(TestCase):
    def setUp(self):
        self.leader = create_role_user("choir-lead", "choir_leader")
        self.member_user = create_role_user("choir-user", "choir_member")
        self.member = Member.objects.create(
            user=self.member_user,
            first_name="Active",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        self.enrollment = ChoirEnrollment.objects.create(
            member=self.member,
            voice_part=ChoirEnrollment.VoicePart.ALTO,
        )

    def test_choir_leader_can_enroll_member(self):
        candidate = Member.objects.create(
            first_name="New",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        self.client.force_login(self.leader)
        response = self.client.post(
            reverse("worship:choir-enroll"),
            {
                "member": candidate.pk,
                "voice_part": ChoirEnrollment.VoicePart.TENOR,
                "status": ChoirEnrollment.Status.ACTIVE,
                "joined_on": timezone.localdate(),
                "notes": "",
            },
        )
        self.assertRedirects(response, reverse("worship:choir-roster"))
        self.assertTrue(ChoirEnrollment.objects.filter(member=candidate).exists())

    def test_choir_member_cannot_access_roster_or_enrollment(self):
        self.client.force_login(self.member_user)
        self.assertEqual(
            self.client.get(reverse("worship:choir-roster")).status_code, 403
        )
        self.assertEqual(
            self.client.get(reverse("worship:choir-enroll")).status_code, 403
        )

    def test_leader_schedules_rehearsal_and_records_attendance(self):
        start = future_datetime()
        self.client.force_login(self.leader)
        response = self.client.post(
            reverse("worship:rehearsal-add"),
            {
                "title": "Weekly rehearsal",
                "starts_at": start.strftime("%Y-%m-%dT%H:%M"),
                "ends_at": (start + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
                "location": "Sanctuary",
                "status": Rehearsal.Status.SCHEDULED,
                "notes": "",
            },
        )
        rehearsal = Rehearsal.objects.get(title="Weekly rehearsal")
        self.assertRedirects(
            response,
            reverse("worship:rehearsal-detail", args=(rehearsal.public_id,)),
        )
        response = self.client.post(
            reverse("worship:rehearsal-attendance", args=(rehearsal.public_id,)),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-enrollment": str(self.enrollment.pk),
                "form-0-status": RehearsalAttendance.Status.PRESENT,
                "form-0-notes": "On time",
            },
        )
        self.assertRedirects(
            response,
            reverse("worship:rehearsal-detail", args=(rehearsal.public_id,)),
        )
        attendance = RehearsalAttendance.objects.get()
        self.assertEqual(attendance.enrollment, self.enrollment)
        self.assertEqual(attendance.recorded_by, self.leader)

    def test_member_sees_member_announcement_not_leader_announcement(self):
        ChoirAnnouncement.objects.create(
            title="Member notice",
            body="Visible",
            audience=ChoirAnnouncement.Audience.MEMBERS,
            created_by=self.leader,
        )
        ChoirAnnouncement.objects.create(
            title="Leader notice",
            body="Restricted",
            audience=ChoirAnnouncement.Audience.LEADERS,
            created_by=self.leader,
        )
        self.client.force_login(self.member_user)
        response = self.client.get(reverse("worship:announcement-list"))
        self.assertContains(response, "Member notice")
        self.assertNotContains(response, "Leader notice")

    def test_member_sees_only_own_rehearsal_attendance(self):
        other_member = Member.objects.create(
            first_name="Other",
            last_name="Attendee",
            membership_status=Member.Status.MEMBER,
        )
        other_enrollment = ChoirEnrollment.objects.create(member=other_member)
        start = future_datetime()
        rehearsal = Rehearsal.objects.create(
            title="Attendance privacy",
            starts_at=start,
            ends_at=start + timedelta(hours=1),
            created_by=self.leader,
        )
        RehearsalAttendance.objects.create(
            rehearsal=rehearsal,
            enrollment=self.enrollment,
            status=RehearsalAttendance.Status.PRESENT,
        )
        RehearsalAttendance.objects.create(
            rehearsal=rehearsal,
            enrollment=other_enrollment,
            status=RehearsalAttendance.Status.ABSENT,
        )
        self.client.force_login(self.member_user)
        response = self.client.get(
            reverse("worship:rehearsal-detail", args=(rehearsal.public_id,))
        )
        self.assertContains(response, self.member.full_name)
        self.assertNotContains(response, other_member.full_name)

    def test_worship_leader_can_coordinate_schedule_without_announcement_access(self):
        worship_leader = create_role_user("choir-coordinator", "worship_leader")
        ChoirAnnouncement.objects.create(
            title="Choir leader private notice",
            body="Restricted announcement",
            audience=ChoirAnnouncement.Audience.LEADERS,
            created_by=self.leader,
        )
        self.client.force_login(worship_leader)

        response = self.client.get(reverse("worship:choir-activity"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choir overview")
        self.assertContains(response, reverse("worship:rehearsal-list"))
        self.assertNotContains(response, "Choir leader private notice")
        self.assertNotContains(response, reverse("worship:announcement-list"))

    def test_choir_dashboard_discloses_only_members_own_assignments(self):
        other_user = create_role_user("other-choir-user", "choir_member")
        other_member = Member.objects.create(
            user=other_user,
            first_name="Other",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        other_enrollment = ChoirEnrollment.objects.create(member=other_member)
        plan = WorshipPlan.objects.create(
            title="Assignment privacy service",
            service_datetime=future_datetime(3),
        )
        PlanChoirParticipation.objects.create(
            plan=plan,
            enrollment=self.enrollment,
        )
        PlanChoirParticipation.objects.create(
            plan=plan,
            enrollment=other_enrollment,
        )
        own_song = Song.objects.create(title="Member preparation song")
        other_song = Song.objects.create(title="Other private song")
        own_plan_song = PlanSong.objects.create(
            plan=plan,
            song=own_song,
            position=1,
        )
        other_plan_song = PlanSong.objects.create(
            plan=plan,
            song=other_song,
            position=2,
        )
        SongAssignment.objects.create(
            plan_song=own_plan_song,
            enrollment=self.enrollment,
            assigned_by=self.leader,
        )
        SongAssignment.objects.create(
            plan_song=other_plan_song,
            enrollment=other_enrollment,
            assigned_by=self.leader,
        )
        self.client.force_login(self.member_user)

        response = self.client.get(reverse("worship:choir-activity"))

        self.assertContains(response, own_song.title)
        self.assertNotContains(response, other_song.title)

    def test_roster_filters_preserve_truthful_membership_summary(self):
        leave_member = Member.objects.create(
            first_name="Leave",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        ChoirEnrollment.objects.create(
            member=leave_member,
            voice_part=ChoirEnrollment.VoicePart.TENOR,
            status=ChoirEnrollment.Status.ON_LEAVE,
        )
        self.client.force_login(self.leader)

        response = self.client.get(
            reverse("worship:choir-roster"),
            {"status": ChoirEnrollment.Status.ON_LEAVE, "voice_part": "tenor"},
        )

        self.assertContains(response, leave_member.full_name)
        self.assertNotContains(response, self.member.full_name)
        self.assertEqual(response.context["roster_summary"]["total"], 2)
        self.assertEqual(response.context["roster_summary"]["active"], 1)
        self.assertEqual(response.context["roster_summary"]["on_leave"], 1)

    def test_rehearsal_directory_segments_upcoming_and_previous(self):
        upcoming = Rehearsal.objects.create(
            title="Upcoming preparation",
            starts_at=future_datetime(),
            ends_at=future_datetime() + timedelta(hours=1),
            created_by=self.leader,
        )
        past_start = timezone.now() - timedelta(days=2)
        previous = Rehearsal.objects.create(
            title="Previous preparation",
            starts_at=past_start,
            ends_at=past_start + timedelta(hours=1),
            status=Rehearsal.Status.COMPLETED,
            created_by=self.leader,
        )
        self.client.force_login(self.member_user)

        upcoming_response = self.client.get(reverse("worship:rehearsal-list"))
        previous_response = self.client.get(
            reverse("worship:rehearsal-list"), {"timing": "past"}
        )

        self.assertContains(upcoming_response, upcoming.title)
        self.assertNotContains(upcoming_response, previous.title)
        self.assertContains(previous_response, previous.title)
        self.assertNotContains(previous_response, upcoming.title)

    def test_announcement_manager_can_filter_scheduled_notices(self):
        ChoirAnnouncement.objects.create(
            title="Current choir notice",
            body="Current",
            created_by=self.leader,
        )
        ChoirAnnouncement.objects.create(
            title="Scheduled choir notice",
            body="Scheduled",
            published_at=timezone.now() + timedelta(days=2),
            created_by=self.leader,
        )
        self.client.force_login(self.leader)

        response = self.client.get(
            reverse("worship:announcement-list"), {"timing": "scheduled"}
        )

        self.assertContains(response, "Scheduled choir notice")
        self.assertNotContains(response, "Current choir notice")

    def test_choir_management_forms_render_for_leader(self):
        start = future_datetime()
        rehearsal = Rehearsal.objects.create(
            title="Form rehearsal",
            starts_at=start,
            ends_at=start + timedelta(hours=1),
            created_by=self.leader,
        )
        self.client.force_login(self.leader)

        enrollment_response = self.client.get(reverse("worship:choir-enroll"))
        rehearsal_response = self.client.get(reverse("worship:rehearsal-add"))
        attendance_response = self.client.get(
            reverse("worship:rehearsal-attendance", args=(rehearsal.public_id,))
        )
        announcement_response = self.client.get(reverse("worship:announcement-add"))

        self.assertContains(enrollment_response, 'id="choir-enrollment-form"')
        self.assertContains(rehearsal_response, 'id="rehearsal-form"')
        self.assertContains(attendance_response, 'id="rehearsal-attendance-form"')
        self.assertContains(announcement_response, 'id="announcement-form"')


class SongLibraryWorkflowTests(TestCase):
    def setUp(self):
        self.leader = create_role_user("worship-song-lead", "worship_leader")
        self.choir_member = create_role_user("song-viewer", "choir_member")

    def test_worship_leader_creates_normalized_song_metadata(self):
        self.client.force_login(self.leader)
        response = self.client.post(
            reverse("worship:song-add"),
            {
                "title": "Grace Song",
                "artist": "Example Artist",
                "default_key": "G",
                "tempo_bpm": "78",
                "category": Song.Category.CONTEMPORARY,
                "themes": [
                    Theme.objects.get(code=code, tradition=None).pk
                    for code in ("grace", "hope")
                ],
                "notes": "",
            },
        )
        song = Song.objects.get(title="Grace Song")
        self.assertRedirects(
            response, reverse("worship:song-detail", args=(song.public_id,))
        )
        self.assertEqual(song.theme_text, "Grace, Hope")
        self.assertEqual(song.created_by, self.leader)

    def test_song_search_filter_and_sort(self):
        Song.objects.create(
            title="Alpha Hope",
            artist="Zulu",
            category=Song.Category.HYMN,
        ).themes.add(Theme.objects.get(code="hope", tradition=None))
        Song.objects.create(
            title="Beta Joy",
            artist="Alpha",
            category=Song.Category.GOSPEL,
        ).themes.add(Theme.objects.get(code="joy", tradition=None))
        self.client.force_login(self.choir_member)
        response = self.client.get(
            reverse("worship:song-list"),
            {"category": Song.Category.HYMN, "theme": "hope", "sort": "artist"},
        )
        self.assertContains(response, "Alpha Hope")
        self.assertNotContains(response, "Beta Joy")

    def test_protected_resource_requires_permission_and_downloads_for_member(self):
        song = Song.objects.create(title="Resource song", category=Song.Category.HYMN)
        with (
            TemporaryDirectory() as media_root,
            override_settings(PROTECTED_MEDIA_ROOT=media_root),
        ):
            resource = SongResource.objects.create(
                song=song,
                title="Chord sheet",
                resource_type=SongResource.ResourceType.CHORD_SHEET,
                file=SimpleUploadedFile("chart.pdf", b"test chart"),
                authorization_reference="Licensed test resource",
                added_by=self.leader,
            )
            ordinary = User.objects.create_user("ordinary-resource", password=PASSWORD)
            self.client.force_login(ordinary)
            denied = self.client.get(
                reverse("worship:song-resource-download", args=(resource.pk,))
            )
            self.assertEqual(denied.status_code, 403)

            self.client.force_login(self.choir_member)
            allowed = self.client.get(
                reverse("worship:song-resource-download", args=(resource.pk,))
            )
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(b"".join(allowed.streaming_content), b"test chart")


class WorshipPlanningWorkflowTests(TestCase):
    def setUp(self):
        self.worship_leader = create_role_user("planner", "worship_leader")
        self.choir_leader = create_role_user("assignment-lead", "choir_leader")
        self.member_user = create_role_user("plan-singer", "choir_member")
        self.other_user = create_role_user("other-singer", "choir_member")
        self.member = Member.objects.create(
            user=self.member_user,
            first_name="Plan",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        self.other_member = Member.objects.create(
            user=self.other_user,
            first_name="Other",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        self.enrollment = ChoirEnrollment.objects.create(member=self.member)
        self.other_enrollment = ChoirEnrollment.objects.create(member=self.other_member)
        self.song_one = Song.objects.create(
            title="First Song",
            category=Song.Category.CONTEMPORARY,
        )
        self.song_two = Song.objects.create(
            title="Second Song",
            category=Song.Category.GOSPEL,
        )
        self.plan = WorshipPlan.objects.create(
            title="Sunday Worship",
            service_datetime=future_datetime(2),
            created_by=self.worship_leader,
        )
        PlanChoirParticipation.objects.create(
            plan=self.plan,
            enrollment=self.enrollment,
        )

    def test_worship_leader_creates_plan_with_participants(self):
        self.client.force_login(self.worship_leader)
        response = self.client.post(
            reverse("worship:plan-add"),
            {
                "title": "Evening Worship",
                "service_theme": Theme.objects.get(code="grace", tradition=None).pk,
                "service_datetime": future_datetime(3).strftime("%Y-%m-%dT%H:%M"),
                "location": "Main hall",
                "status": WorshipPlan.Status.PREPARING,
                "preparation_notes": "Prepare transitions",
                "choir_participants": [str(self.enrollment.pk)],
            },
        )
        created = WorshipPlan.objects.get(title="Evening Worship")
        self.assertRedirects(
            response, reverse("worship:plan-detail", args=(created.public_id,))
        )
        self.assertTrue(
            created.choir_participants.filter(pk=self.enrollment.pk).exists()
        )

    def test_setlist_add_and_reorder(self):
        first = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        second = PlanSong.objects.create(plan=self.plan, song=self.song_two, position=2)
        self.assertTrue(move_plan_song(plan_song=second, direction="up"))
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual((second.position, first.position), (1, 2))

    def test_choir_leader_assigns_only_plan_participants(self):
        item = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        self.client.force_login(self.choir_leader)
        response = self.client.post(
            reverse("worship:song-assignments", args=(self.plan.public_id, item.pk)),
            {"enrollments": [str(self.enrollment.pk)], "notes": "Lead melody"},
        )
        self.assertRedirects(
            response, reverse("worship:plan-detail", args=(self.plan.public_id,))
        )
        assignment = SongAssignment.objects.get()
        self.assertEqual(assignment.enrollment, self.enrollment)
        self.assertEqual(assignment.assigned_by, self.choir_leader)

        response = self.client.post(
            reverse("worship:song-assignments", args=(self.plan.public_id, item.pk)),
            {"enrollments": [str(self.other_enrollment.pk)], "notes": "Invalid"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            SongAssignment.objects.filter(enrollment=self.other_enrollment).exists()
        )

        response = self.client.post(
            reverse("worship:song-assignments", args=(self.plan.public_id, item.pk)),
            {"enrollments": [str(self.enrollment.pk)], "notes": ""},
        )
        self.assertRedirects(
            response,
            reverse("worship:plan-detail", args=(self.plan.public_id,)),
        )
        assignment.refresh_from_db()
        self.assertEqual(assignment.notes, "")

    def test_choir_member_sees_only_participating_plan(self):
        hidden_plan = WorshipPlan.objects.create(
            title="Hidden Plan",
            service_datetime=future_datetime(4),
        )
        self.client.force_login(self.member_user)
        list_response = self.client.get(reverse("worship:plan-list"))
        self.assertContains(list_response, self.plan.title)
        self.assertNotContains(list_response, hidden_plan.title)
        detail_response = self.client.get(
            reverse("worship:plan-detail", args=(hidden_plan.public_id,))
        )
        self.assertEqual(detail_response.status_code, 404)

    def test_member_detail_does_not_disclose_other_assignments(self):
        PlanChoirParticipation.objects.create(
            plan=self.plan,
            enrollment=self.other_enrollment,
        )
        item = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        SongAssignment.objects.create(plan_song=item, enrollment=self.enrollment)
        SongAssignment.objects.create(plan_song=item, enrollment=self.other_enrollment)
        self.client.force_login(self.member_user)
        response = self.client.get(
            reverse("worship:plan-detail", args=(self.plan.public_id,))
        )
        self.assertContains(response, self.member.full_name)
        self.assertNotContains(response, self.other_member.full_name)

    def test_song_usage_history_respects_plan_object_access(self):
        hidden_plan = WorshipPlan.objects.create(
            title="Private Leader Plan",
            service_datetime=future_datetime(4),
        )
        PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        PlanSong.objects.create(plan=hidden_plan, song=self.song_one, position=1)
        self.client.force_login(self.member_user)
        response = self.client.get(
            reverse("worship:song-detail", args=(self.song_one.public_id,))
        )
        self.assertContains(response, self.plan.title)
        self.assertNotContains(response, hidden_plan.title)

    def test_removing_participant_removes_their_song_assignments(self):
        item = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        SongAssignment.objects.create(plan_song=item, enrollment=self.enrollment)
        sync_plan_participants(plan=self.plan, enrollments=[])
        self.assertFalse(self.plan.choir_participations.exists())
        self.assertFalse(SongAssignment.objects.exists())

    def test_ordinary_user_cannot_manage_plans(self):
        ordinary = User.objects.create_user("ordinary-planner", password=PASSWORD)
        self.client.force_login(ordinary)
        self.assertEqual(self.client.get(reverse("worship:plan-add")).status_code, 403)

    def test_plan_directory_segments_status_and_scoped_counts(self):
        ready_plan = WorshipPlan.objects.create(
            title="Ready evening worship",
            service_datetime=future_datetime(3),
            status=WorshipPlan.Status.READY,
            created_by=self.worship_leader,
        )
        previous_plan = WorshipPlan.objects.create(
            title="Previous worship",
            service_datetime=timezone.now() - timedelta(days=7),
            status=WorshipPlan.Status.COMPLETED,
            created_by=self.worship_leader,
        )
        self.client.force_login(self.worship_leader)

        upcoming_response = self.client.get(
            reverse("worship:plan-list"), {"status": WorshipPlan.Status.READY}
        )
        previous_response = self.client.get(
            reverse("worship:plan-list"), {"timing": "previous"}
        )

        self.assertContains(upcoming_response, ready_plan.title)
        self.assertNotContains(upcoming_response, self.plan.title)
        self.assertNotContains(upcoming_response, previous_plan.title)
        self.assertContains(previous_response, previous_plan.title)
        self.assertNotContains(previous_response, ready_plan.title)
        self.assertEqual(upcoming_response.context["plan_summary"]["all"], 3)
        self.assertEqual(upcoming_response.context["plan_summary"]["ready"], 1)

    def test_member_plan_screen_hides_management_and_other_assignments(self):
        PlanChoirParticipation.objects.create(
            plan=self.plan,
            enrollment=self.other_enrollment,
        )
        item = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        SongAssignment.objects.create(plan_song=item, enrollment=self.enrollment)
        SongAssignment.objects.create(plan_song=item, enrollment=self.other_enrollment)
        self.client.force_login(self.member_user)

        response = self.client.get(
            reverse("worship:plan-detail", args=(self.plan.public_id,))
        )

        self.assertContains(response, self.member.full_name)
        self.assertNotContains(response, self.other_member.full_name)
        self.assertNotContains(
            response, reverse("worship:plan-edit", args=(self.plan.public_id,))
        )
        self.assertNotContains(
            response, reverse("worship:plan-song-add", args=(self.plan.public_id,))
        )
        self.assertNotContains(response, "Move up")
        self.assertNotContains(response, "Remove")

    def test_setlist_move_and_remove_endpoints_preserve_order(self):
        first = PlanSong.objects.create(plan=self.plan, song=self.song_one, position=1)
        second = PlanSong.objects.create(plan=self.plan, song=self.song_two, position=2)
        self.client.force_login(self.worship_leader)

        move_response = self.client.post(
            reverse(
                "worship:plan-song-move",
                args=(self.plan.public_id, second.pk, "up"),
            )
        )
        remove_response = self.client.post(
            reverse(
                "worship:plan-song-remove",
                args=(self.plan.public_id, first.pk),
            )
        )

        self.assertRedirects(
            move_response,
            reverse("worship:plan-detail", args=(self.plan.public_id,)),
        )
        self.assertRedirects(
            remove_response,
            reverse("worship:plan-detail", args=(self.plan.public_id,)),
        )
        second.refresh_from_db()
        self.assertEqual(second.position, 1)
        self.assertFalse(PlanSong.objects.filter(pk=first.pk).exists())

    def test_plan_forms_render_refined_workflows(self):
        self.client.force_login(self.worship_leader)

        plan_response = self.client.get(reverse("worship:plan-add"))
        song_response = self.client.get(
            reverse("worship:plan-song-add", args=(self.plan.public_id,))
        )

        self.assertContains(plan_response, 'id="worship-plan-form"')
        self.assertContains(song_response, 'id="plan-song-form"')
        self.assertContains(song_response, self.plan.title)

    def test_plan_creation_uses_linked_worship_event_schedule(self):
        event_start = future_datetime(5)
        event = Event.objects.create(
            title="Linked Sunday service",
            event_type=Event.Type.WORSHIP_SERVICE,
            starts_at=event_start,
            ends_at=event_start + timedelta(hours=2),
            location="Main sanctuary",
            status=Event.Status.PUBLISHED,
            visibility=Event.Visibility.CHURCH,
            created_by=self.worship_leader,
        )
        self.client.force_login(self.worship_leader)

        response = self.client.post(
            reverse("worship:plan-add"),
            {
                "event": event.pk,
                "title": "Event-linked plan",
                "service_theme": Theme.objects.get(code="grace", tradition=None).pk,
                "service_datetime": "",
                "location": "",
                "status": WorshipPlan.Status.PREPARING,
                "preparation_notes": "Use the event schedule",
                "choir_participants": [str(self.enrollment.pk)],
            },
        )

        created = WorshipPlan.objects.get(title="Event-linked plan")
        self.assertRedirects(
            response, reverse("worship:plan-detail", args=(created.public_id,))
        )
        self.assertEqual(created.event, event)
        self.assertEqual(created.service_datetime, event.starts_at)
        self.assertEqual(created.location, event.location)

    def test_ordinary_user_cannot_view_plan_direct_url(self):
        ordinary = User.objects.create_user("ordinary-plan-viewer", password=PASSWORD)
        self.client.force_login(ordinary)

        response = self.client.get(
            reverse("worship:plan-detail", args=(self.plan.public_id,))
        )

        self.assertEqual(response.status_code, 403)
