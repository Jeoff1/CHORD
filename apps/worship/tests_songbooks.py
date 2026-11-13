from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.traditions import services
from apps.traditions.models import Tradition

from .models import Song, Songbook, SongResource, WorshipPlan

PASSWORD = "Correct-Horse-47-Battery"


def activate(code):
    profile = services.get_church_profile()
    profile.tradition = Tradition.objects.get(code=code)
    profile.save()


class AllowedSongbooksTests(TestCase):
    def codes(self):
        return {songbook.code for songbook in services.allowed_songbooks()}

    def test_each_preset_allows_its_own_songbooks(self):
        expected = {
            "alliance": {"general"},
            "roman-catholic": {"general", "catholic-hymnal"},
            "iglesia-ni-cristo": {"inc-hymnal"},
        }
        for code, songbooks in expected.items():
            with self.subTest(tradition=code):
                activate(code)
                self.assertEqual(self.codes(), songbooks)


def song_in(songbook_code, title, **extra):
    return Song.objects.create(
        title=title,
        category=Song.Category.HYMN,
        songbook=Songbook.objects.get(code=songbook_code),
        **extra,
    )


class WorshipLeaderTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user("leader", password=PASSWORD)
        UserRole.objects.create(user=user, role=Role.objects.get(code="worship_leader"))
        self.client.force_login(user)


class SetlistSongbookFilterTests(WorshipLeaderTestCase):
    def setUp(self):
        super().setUp()
        activate("alliance")
        self.allowed = song_in("general", "Amazing Grace")
        self.disallowed = song_in("inc-hymnal", "INC Hymn 1")
        self.plan = WorshipPlan.objects.create(
            title="Sunday", service_datetime=timezone.now() + timedelta(days=1)
        )
        self.url = reverse("worship:plan-song-add", args=(self.plan.public_id,))

    def test_form_offers_only_songs_from_allowed_songbooks(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Amazing Grace")
        self.assertNotContains(response, "INC Hymn 1")

    def test_posting_a_disallowed_song_is_refused(self):
        response = self.client.post(self.url, {"song": self.disallowed.pk})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.plan.setlist_items.exists())

    def test_posting_an_allowed_song_adds_it(self):
        self.client.post(self.url, {"song": self.allowed.pk})
        self.assertTrue(self.plan.setlist_items.filter(song=self.allowed).exists())


class MetadataOnlyResourceTests(WorshipLeaderTestCase):
    def post_resource(self, song, resource_type):
        return self.client.post(
            reverse("worship:song-resource-add", args=(song.public_id,)),
            {
                "title": "Sheet",
                "resource_type": resource_type,
                "external_url": "https://example.com/sheet",
                "authorization_reference": "CCLI 123",
            },
        )

    def test_songs_in_a_metadata_only_songbook_refuse_lyrics_and_sheets(self):
        song = song_in("inc-hymnal", "INC Hymn 1")
        for resource_type in ("lyrics", "chord_sheet", "lead_sheet"):
            with self.subTest(resource_type=resource_type):
                response = self.post_resource(song, resource_type)
                self.assertContains(response, "metadata only")
        self.assertFalse(SongResource.objects.exists())

    def test_a_song_flagged_metadata_only_refuses_lyrics(self):
        song = song_in("general", "Copyrighted Song", metadata_only=True)
        self.assertContains(self.post_resource(song, "lyrics"), "metadata only")
        self.assertFalse(SongResource.objects.exists())

    def test_metadata_only_songs_still_accept_reference_audio(self):
        song = song_in("inc-hymnal", "INC Hymn 1")
        self.post_resource(song, "reference_audio")
        self.assertTrue(song.resources.exists())

    def test_ordinary_songs_accept_lyrics(self):
        song = song_in("general", "Amazing Grace")
        self.post_resource(song, "lyrics")
        self.assertTrue(song.resources.exists())


class SongFormSongbookTests(WorshipLeaderTestCase):
    def create_song(self, **extra):
        self.client.post(
            reverse("worship:song-add"),
            {"title": "New Hymn", "category": Song.Category.HYMN, **extra},
        )
        return Song.objects.get(title="New Hymn")

    def test_blank_songbook_uses_the_traditions_default(self):
        activate("iglesia-ni-cristo")
        self.assertEqual(self.create_song().songbook.code, "inc-hymnal")

    def test_blank_songbook_prefers_a_full_content_songbook(self):
        activate("roman-catholic")
        self.assertEqual(self.create_song().songbook.code, "general")

    def test_leader_can_choose_a_songbook(self):
        activate("alliance")
        chosen = Songbook.objects.get(code="catholic-hymnal")
        self.assertEqual(self.create_song(songbook=chosen.pk).songbook, chosen)
