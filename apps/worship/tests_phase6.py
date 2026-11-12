import os
from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.members.models import Member

from .chordpro import parse_chordpro
from .forms import SongForm
from .models import (
    ChoirEnrollment,
    PlanChoirParticipation,
    PlanSong,
    Rehearsal,
    Song,
    SongAssignment,
    SongResource,
    WorshipPlan,
)
from .spotify import normalize_spotify_track

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"
SPOTIFY_TRACK_ID = "0Lr4kGOYn9l83EjuK6cZFQ"


def create_role_user(username, role_code):
    user = User.objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


def future_datetime(days=1):
    return timezone.now().replace(second=0, microsecond=0) + timedelta(days=days)


class SpotifyValidationTests(TestCase):
    def test_supported_spotify_track_inputs_are_normalized(self):
        supported = (
            SPOTIFY_TRACK_ID,
            f"spotify:track:{SPOTIFY_TRACK_ID}",
            f"https://open.spotify.com/track/{SPOTIFY_TRACK_ID}?si=test",
            f"https://open.spotify.com/embed/track/{SPOTIFY_TRACK_ID}",
            f"https://open.spotify.com/intl-de/track/{SPOTIFY_TRACK_ID}",
        )
        for value in supported:
            with self.subTest(value=value):
                self.assertEqual(normalize_spotify_track(value), SPOTIFY_TRACK_ID)

    def test_unsupported_spotify_inputs_are_rejected(self):
        unsupported = (
            f"http://open.spotify.com/track/{SPOTIFY_TRACK_ID}",
            f"https://example.com/track/{SPOTIFY_TRACK_ID}",
            f"https://open.spotify.com/album/{SPOTIFY_TRACK_ID}",
            f"https://open.spotify.com:invalid/track/{SPOTIFY_TRACK_ID}",
            f"spotify:album:{SPOTIFY_TRACK_ID}",
            "short-id",
        )
        for value in unsupported:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_spotify_track(value)

    def test_song_form_stores_only_normalized_track_id(self):
        form = SongForm(
            data={
                "title": "Spotify song",
                "artist": "Artist",
                "default_key": "G",
                "tempo_bpm": "90",
                "category": Song.Category.CONTEMPORARY,
                "theme_list": "hope",
                "spotify_track": (
                    f"https://open.spotify.com/track/{SPOTIFY_TRACK_ID}?si=test"
                ),
                "notes": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        song = form.save()
        self.assertEqual(song.spotify_track_id, SPOTIFY_TRACK_ID)
        self.assertEqual(
            song.spotify_embed_url,
            f"https://open.spotify.com/embed/track/{SPOTIFY_TRACK_ID}",
        )

    def test_song_create_rejects_album_link_and_renders_embed_for_track(self):
        leader = create_role_user("spotify-leader", "worship_leader")
        self.client.force_login(leader)
        base_data = {
            "title": "Embedded song",
            "artist": "Artist",
            "default_key": "C",
            "tempo_bpm": "80",
            "category": Song.Category.HYMN,
            "theme_list": "grace",
            "notes": "",
        }
        response = self.client.post(
            reverse("worship:song-add"),
            base_data
            | {"spotify_track": f"https://open.spotify.com/album/{SPOTIFY_TRACK_ID}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Song.objects.filter(title="Embedded song").exists())

        response = self.client.post(
            reverse("worship:song-add"),
            base_data | {"spotify_track": f"spotify:track:{SPOTIFY_TRACK_ID}"},
        )
        song = Song.objects.get(title="Embedded song")
        self.assertRedirects(
            response,
            reverse("worship:song-detail", args=(song.public_id,)),
        )
        detail = self.client.get(reverse("worship:song-detail", args=(song.public_id,)))
        self.assertContains(detail, song.spotify_embed_url)
        self.assertContains(detail, "Playback availability")


class ChordProParserTests(TestCase):
    def test_parser_returns_structured_safe_data(self):
        parsed = parse_chordpro(
            "{title: Grace}\n{key: G}\n{start_of_chorus}\n[G]Grace [C]abounds"
        )
        self.assertIn(("Title", "Grace"), parsed["metadata"])
        self.assertIn(("Key", "G"), parsed["metadata"])
        self.assertEqual(parsed["blocks"][0]["text"], "Chorus")
        self.assertEqual(parsed["blocks"][1]["segments"][0]["chord"], "G")

    def test_parser_transposes_chords_and_key_by_semitones(self):
        parsed = parse_chordpro(
            "{key: G}\n[G]Grace [Em7]so [C/E]free [N.C.]now", semitones=3
        )
        self.assertIn(("Key", "Bb"), parsed["metadata"])
        chords = [s["chord"] for s in parsed["blocks"][0]["segments"]]
        self.assertEqual(chords, ["Bb", "Gm7", "Eb/G", "N.C."])

    def test_parser_transposes_down_with_wraparound(self):
        parsed = parse_chordpro("[C]Grace [F#m]now", semitones=-2)
        chords = [s["chord"] for s in parsed["blocks"][0]["segments"]]
        self.assertEqual(chords, ["Bb", "Em"])

    def test_parser_leaves_annotation_brackets_untransposed(self):
        parsed = parse_chordpro("[Bridge]Grace [Esus4]now [Cmaj7]free", semitones=1)
        chords = [s["chord"] for s in parsed["blocks"][0]["segments"]]
        self.assertEqual(chords, ["Bridge", "Fsus4", "Dbmaj7"])


class SongResourcePhaseSixTests(TestCase):
    def setUp(self):
        self.leader = create_role_user("resource-leader", "worship_leader")
        self.choir_member = create_role_user("resource-member", "choir_member")
        self.ordinary = User.objects.create_user("resource-ordinary", password=PASSWORD)
        self.song = Song.objects.create(
            title="Resource song", category=Song.Category.HYMN
        )

    def create_file_resource(self, filename, content):
        return SongResource.objects.create(
            song=self.song,
            title="Authorized chart",
            resource_type=SongResource.ResourceType.CHORD_SHEET,
            file=SimpleUploadedFile(filename, content),
            authorization_reference="Church license",
            added_by=self.leader,
            updated_by=self.leader,
        )

    def test_pdf_preview_is_inline_and_permission_checked(self):
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource("chart.pdf", b"%PDF-test")
            self.client.force_login(self.ordinary)
            denied = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,))
            )
            self.assertEqual(denied.status_code, 403)

            self.client.force_login(self.choir_member)
            allowed = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,))
            )
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed["Content-Type"], "application/pdf")
            self.assertIn("inline", allowed["Content-Disposition"])
            self.assertEqual(allowed["X-Content-Type-Options"], "nosniff")
            self.assertEqual(b"".join(allowed.streaming_content), b"%PDF-test")

    def test_text_preview_escapes_uploaded_content(self):
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource(
                "chart.txt", b"<script>alert('unsafe')</script>\nG C D"
            )
            self.client.force_login(self.choir_member)
            response = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,))
            )
            self.assertContains(response, "&lt;script&gt;", html=False)
            self.assertNotContains(response, "<script>alert")

    def test_chordpro_preview_formats_metadata_and_chords(self):
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource(
                "chart.chordpro",
                b"{title: Grace}\n{key: G}\n[G]Grace [C]abounds",
            )
            self.client.force_login(self.choir_member)
            response = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,))
            )
            self.assertContains(response, "Grace")
            self.assertContains(response, "Key")
            self.assertContains(response, ">G<", html=False)
            self.assertContains(response, ">C<", html=False)

    def test_chordpro_preview_transposes_to_setlist_planned_key(self):
        self.song.default_key = "G"
        self.song.save()
        plan = WorshipPlan.objects.create(
            title="Transposed service", service_datetime=future_datetime(2)
        )
        plan_song = PlanSong.objects.create(
            plan=plan, song=self.song, position=1, planned_key="A"
        )
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource(
                "chart.chordpro", b"{key: G}\n[G]Grace [C]abounds"
            )
            url = reverse("worship:song-resource-preview", args=(resource.pk,))
            self.client.force_login(self.leader)

            planned = self.client.get(url, {"plan_song": plan_song.pk})
            self.assertContains(planned, ">A<", html=False)
            self.assertContains(planned, ">D<", html=False)
            self.assertNotContains(planned, ">G<", html=False)

            shifted = self.client.get(
                url, {"plan_song": plan_song.pk, "transpose": "-2"}
            )
            self.assertContains(shifted, ">F<", html=False)
            self.assertContains(shifted, ">Bb<", html=False)

            untouched = self.client.get(url, {"transpose": "not-a-number"})
            self.assertContains(untouched, ">G<", html=False)

    def test_chordpro_preview_ignores_plan_the_viewer_cannot_see(self):
        self.song.default_key = "G"
        self.song.save()
        plan = WorshipPlan.objects.create(
            title="Private service", service_datetime=future_datetime(2)
        )
        plan_song = PlanSong.objects.create(
            plan=plan, song=self.song, position=1, planned_key="A"
        )
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource("chart.chordpro", b"[G]Grace")
            self.client.force_login(self.choir_member)
            response = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,)),
                {"plan_song": plan_song.pk},
            )
            self.assertContains(response, ">G<", html=False)
            self.assertNotContains(response, ">A<", html=False)

    def test_unsupported_word_preview_has_download_fallback(self):
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource("chart.docx", b"test")
            self.client.force_login(self.choir_member)
            response = self.client.get(
                reverse("worship:song-resource-preview", args=(resource.pk,))
            )
            self.assertContains(response, "cannot be displayed safely")
            self.assertContains(response, "Download original")

    def test_worship_leader_can_replace_resource_and_old_file_is_removed(self):
        with (
            TemporaryDirectory() as protected_root,
            override_settings(PROTECTED_MEDIA_ROOT=protected_root),
        ):
            resource = self.create_file_resource("old.txt", b"old")
            old_path = resource.file.path
            self.assertTrue(os.path.exists(old_path))
            self.client.force_login(self.leader)
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    reverse("worship:song-resource-edit", args=(resource.pk,)),
                    {
                        "title": "Replacement chart",
                        "resource_type": SongResource.ResourceType.CHORD_SHEET,
                        "file": SimpleUploadedFile("new.chordpro", b"[G]New"),
                        "external_url": "",
                        "authorization_reference": "Updated church license",
                    },
                )
            self.assertRedirects(
                response,
                reverse("worship:song-detail", args=(self.song.public_id,)),
            )
            resource.refresh_from_db()
            self.assertEqual(resource.updated_by, self.leader)
            self.assertTrue(resource.file.name.endswith("new.chordpro"))
            self.assertFalse(os.path.exists(old_path))
            self.assertTrue(os.path.exists(resource.file.path))

    def test_choir_member_cannot_edit_resource(self):
        resource = SongResource.objects.create(
            song=self.song,
            title="External chart",
            resource_type=SongResource.ResourceType.CHORD_SHEET,
            external_url="https://example.com/authorized-chart",
            authorization_reference="Publisher permission",
            added_by=self.leader,
        )
        self.client.force_login(self.choir_member)
        response = self.client.get(
            reverse("worship:song-resource-edit", args=(resource.pk,))
        )
        self.assertEqual(response.status_code, 403)


class ResourceIntegrationTests(TestCase):
    def setUp(self):
        self.choir_leader = create_role_user("prep-leader", "choir_leader")
        self.member_user = create_role_user("prep-member", "choir_member")
        self.member = Member.objects.create(
            user=self.member_user,
            first_name="Prepared",
            last_name="Singer",
            membership_status=Member.Status.MEMBER,
        )
        self.enrollment = ChoirEnrollment.objects.create(member=self.member)
        self.song = Song.objects.create(
            title="Preparation song",
            category=Song.Category.CONTEMPORARY,
            spotify_track_id=SPOTIFY_TRACK_ID,
        )
        self.resource = SongResource.objects.create(
            song=self.song,
            title="Preparation chart",
            resource_type=SongResource.ResourceType.CHORD_SHEET,
            external_url="https://example.com/preparation-chart",
            authorization_reference="Publisher permission",
            added_by=self.choir_leader,
        )

    def test_rehearsal_detail_exposes_selected_song_resources(self):
        rehearsal = Rehearsal.objects.create(
            title="Preparation rehearsal",
            starts_at=future_datetime(),
            ends_at=future_datetime() + timedelta(hours=2),
        )
        rehearsal.songs.add(self.song)
        self.client.force_login(self.member_user)
        response = self.client.get(
            reverse("worship:rehearsal-detail", args=(rehearsal.public_id,))
        )
        self.assertContains(response, self.song.title)
        self.assertContains(response, self.resource.title)
        self.assertContains(response, "Open on Spotify")

    def test_plan_and_assignment_views_expose_resources(self):
        plan = WorshipPlan.objects.create(
            title="Preparation plan",
            service_datetime=future_datetime(2),
        )
        PlanChoirParticipation.objects.create(plan=plan, enrollment=self.enrollment)
        plan_song = PlanSong.objects.create(plan=plan, song=self.song, position=1)
        SongAssignment.objects.create(
            plan_song=plan_song,
            enrollment=self.enrollment,
            assigned_by=self.choir_leader,
        )
        self.client.force_login(self.member_user)
        plan_response = self.client.get(
            reverse("worship:plan-detail", args=(plan.public_id,))
        )
        self.assertContains(plan_response, self.resource.title)
        activity_response = self.client.get(reverse("worship:choir-activity"))
        self.assertContains(activity_response, self.resource.title)
