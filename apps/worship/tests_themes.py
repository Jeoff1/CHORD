from io import StringIO
from types import SimpleNamespace

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from apps.traditions import services
from apps.traditions.models import Theme
from apps.traditions.theme_matching import match_legacy_themes

from .forms import SongForm
from .models import Song
from .tests_songbooks import WorshipLeaderTestCase, activate


def theme(code, tradition_id=None, name=None):
    return SimpleNamespace(
        code=code, name=name or code.title(), tradition_id=tradition_id
    )


class MatchLegacyThemesTests(TestCase):
    def test_matches_by_code_or_name_ignoring_case_spacing_and_hyphens(self):
        spirit = theme("holy-spirit", name="Holy Spirit")
        grace = theme("grace")
        matched, unmatched = match_legacy_themes(
            [" GRACE ", "holy  spirit", "Holy-Spirit", "revival", "revival"],
            [spirit, grace],
        )
        self.assertEqual(matched, [grace, spirit])
        self.assertEqual(unmatched, ["revival"])

    def test_common_theme_wins_over_tradition_theme(self):
        common = theme("unity")
        local = theme("unity", tradition_id=3)
        matched, _ = match_legacy_themes(["unity"], [local, common])
        self.assertEqual(matched, [common])


class AvailableThemesTests(TestCase):
    def codes(self):
        return {t.code for t in services.available_themes()}

    def test_each_tradition_sees_common_themes_plus_its_own(self):
        own = {
            "roman-catholic": "eucharist",
            "alliance": "missions",
            "iglesia-ni-cristo": "unity",
        }
        for code, theme_code in own.items():
            with self.subTest(tradition=code):
                activate(code)
                codes = self.codes()
                self.assertIn("grace", codes)
                self.assertIn(theme_code, codes)
                for other_code, other in own.items():
                    if other_code != code:
                        self.assertNotIn(other, codes)

    def test_song_form_offers_available_themes(self):
        activate("roman-catholic")
        offered = set(SongForm().fields["themes"].queryset)
        self.assertEqual(offered, set(services.available_themes()))
        self.assertNotIn(Theme.objects.get(code="missions"), offered)


class SongThemeWorkflowTests(WorshipLeaderTestCase):
    def setUp(self):
        super().setUp()
        activate("alliance")
        self.grace = Theme.objects.get(code="grace", tradition=None)
        self.missions = Theme.objects.get(code="missions")

    def post_song(self, themes, song=None):
        url = (
            reverse("worship:song-edit", args=(song.public_id,))
            if song
            else reverse("worship:song-add")
        )
        return self.client.post(
            url,
            {
                "title": "Tagged",
                "category": Song.Category.HYMN,
                "themes": [t.pk for t in themes],
            },
        )

    def test_song_is_tagged_with_chosen_themes(self):
        self.post_song([self.grace, self.missions])
        song = Song.objects.get(title="Tagged")
        self.assertEqual(set(song.themes.all()), {self.grace, self.missions})

    def test_theme_from_another_tradition_is_refused(self):
        eucharist = Theme.objects.get(code="eucharist")
        response = self.post_song([eucharist])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Song.objects.filter(title="Tagged").exists())

    def test_editing_keeps_themes_of_other_traditions(self):
        eucharist = Theme.objects.get(code="eucharist")
        song = Song.objects.create(title="Tagged", category=Song.Category.HYMN)
        song.themes.add(eucharist)
        self.post_song([self.grace], song=song)
        self.assertEqual(set(song.themes.all()), {self.grace, eucharist})

    def test_song_list_filters_by_theme_code(self):
        tagged = Song.objects.create(title="Graceful", category=Song.Category.HYMN)
        tagged.themes.add(self.grace)
        Song.objects.create(title="Untagged", category=Song.Category.HYMN)
        response = self.client.get(reverse("worship:song-list"), {"theme": "grace"})
        self.assertContains(response, "Graceful")
        self.assertNotContains(response, "Untagged")


class ReportUnmatchedThemesTests(TestCase):
    def test_lists_songs_with_unmatched_legacy_themes(self):
        Song.objects.create(
            title="Old Song", category=Song.Category.HYMN, legacy_themes=["revival"]
        )
        Song.objects.create(title="Clean Song", category=Song.Category.HYMN)
        out = StringIO()
        call_command("report_unmatched_themes", stdout=out)
        self.assertIn("Old Song", out.getvalue())
        self.assertIn("revival", out.getvalue())
        self.assertNotIn("Clean Song", out.getvalue())

    def test_reports_nothing_when_all_matched(self):
        out = StringIO()
        call_command("report_unmatched_themes", stdout=out)
        self.assertIn("No unmatched legacy themes", out.getvalue())


class LegacyThemeMigrationTests(TransactionTestCase):
    before = [("worship", "0004_songbooks"), ("traditions", "0006_themes")]
    after = [("worship", "0005_controlled_themes")]

    def tearDown(self):
        MigrationExecutor(connection).migrate(
            MigrationExecutor(connection).loader.graph.leaf_nodes()
        )

    def test_matching_strings_become_themes_and_the_rest_stay_legacy(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.before)
        old_apps = executor.loader.project_state(self.before).apps
        OldSong = old_apps.get_model("worship", "Song")
        OldSong.objects.create(
            title="Legacy", category="hymn", themes=["grace", "holy spirit", "revival"]
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.after)
        new_apps = executor.loader.project_state(self.after).apps
        song = new_apps.get_model("worship", "Song").objects.get(title="Legacy")
        self.assertEqual({t.code for t in song.themes.all()}, {"grace", "holy-spirit"})
        self.assertEqual(song.legacy_themes, ["revival"])
