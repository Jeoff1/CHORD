from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.traditions import services
from apps.traditions.models import Occasion, Season, Theme, Tradition
from apps.worship.models import WorshipPlan
from apps.worship.tests_songbooks import PASSWORD, WorshipLeaderTestCase, activate


def tradition(code):
    return Tradition.objects.get(code=code)


class PresetCalendarTests(TestCase):
    def test_catholic_preset_ships_the_liturgical_seasons(self):
        names = set(
            Season.objects.filter(tradition__code="roman-catholic").values_list(
                "name", flat=True
            )
        )
        self.assertEqual(
            names, {"Advent", "Christmas", "Lent", "Easter", "Ordinary Time"}
        )

    def test_alliance_preset_ships_holidays_and_occasions(self):
        names = set(
            Occasion.objects.filter(tradition__code="alliance").values_list(
                "name", flat=True
            )
        )
        self.assertTrue(
            {"Christmas Day", "Easter Sunday", "Missions Conference"} <= names
        )

    def test_inc_preset_ships_occasions_and_no_seasons(self):
        self.assertFalse(
            Season.objects.filter(tradition__code="iglesia-ni-cristo").exists()
        )
        self.assertTrue(
            Occasion.objects.filter(tradition__code="iglesia-ni-cristo").exists()
        )


class SeasonForDateTests(TestCase):
    def test_returns_the_season_containing_the_date(self):
        activate("roman-catholic")
        self.assertEqual(services.season_for(date(2027, 3, 1)).name, "Lent")
        self.assertEqual(services.season_for(date(2026, 12, 25)).name, "Christmas")

    def test_range_is_inclusive(self):
        activate("roman-catholic")
        lent = Season.objects.get(tradition__code="roman-catholic", name="Lent")
        self.assertEqual(services.season_for(lent.start_date), lent)
        self.assertEqual(services.season_for(lent.end_date), lent)

    def test_returns_none_for_inc(self):
        activate("iglesia-ni-cristo")
        self.assertIsNone(services.season_for(date(2027, 3, 1)))

    def test_returns_none_outside_every_season(self):
        activate("roman-catholic")
        self.assertIsNone(services.season_for(date(1990, 1, 1)))

    def test_uses_only_the_active_tradition(self):
        Season.objects.create(
            tradition=tradition("alliance"),
            name="Missions Month",
            start_date=date(1990, 1, 1),
            end_date=date(1990, 1, 31),
        )
        activate("roman-catholic")
        self.assertIsNone(services.season_for(date(1990, 1, 15)))


class CalendarEntryValidationTests(TestCase):
    def test_end_before_start_is_rejected(self):
        season = Season(
            tradition=tradition("alliance"),
            name="Backwards",
            start_date=date(2030, 2, 1),
            end_date=date(2030, 1, 1),
        )
        with self.assertRaises(ValidationError):
            season.full_clean()

    def test_overlapping_seasons_in_one_tradition_are_rejected(self):
        lent = Season.objects.get(tradition__code="roman-catholic", name="Lent")
        overlap = Season(
            tradition=lent.tradition,
            name="Overlap",
            start_date=lent.start_date,
            end_date=lent.start_date,
        )
        with self.assertRaises(ValidationError):
            overlap.full_clean()


class ChurchAdministratorTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user("admin1", password=PASSWORD)
        UserRole.objects.create(
            user=user, role=Role.objects.get(code="church_administrator")
        )
        self.client.force_login(user)


class CalendarScreenTests(ChurchAdministratorTestCase):
    def test_calendar_lists_the_active_traditions_entries(self):
        activate("roman-catholic")
        response = self.client.get(reverse("traditions:calendar"))
        self.assertContains(response, "Advent")
        self.assertNotContains(response, "Missions Conference")

    def test_inc_calendar_shows_occasions_without_seasons(self):
        activate("iglesia-ni-cristo")
        response = self.client.get(reverse("traditions:calendar"))
        self.assertEqual(list(response.context["seasons"]), [])
        self.assertTrue(response.context["occasions"])

    def test_administrator_edits_a_movable_season(self):
        activate("roman-catholic")
        easter = Season.objects.get(tradition__code="roman-catholic", name="Easter")
        response = self.client.post(
            reverse("traditions:season-edit", args=[easter.pk]),
            {"start_date": "2027-03-28", "end_date": "2027-05-15"},
        )
        self.assertRedirects(response, reverse("traditions:calendar"))
        easter.refresh_from_db()
        self.assertEqual(easter.end_date, date(2027, 5, 15))

    def test_inactive_traditions_entries_cannot_be_edited(self):
        activate("roman-catholic")
        occasion = Occasion.objects.filter(tradition__code="alliance").first()
        response = self.client.post(
            reverse("traditions:occasion-edit", args=[occasion.pk]),
            {"start_date": "2031-06-01", "end_date": "2031-06-03"},
        )
        self.assertEqual(response.status_code, 404)

    def test_administrator_edits_an_occasion(self):
        activate("alliance")
        occasion = Occasion.objects.filter(tradition__code="alliance").first()
        response = self.client.post(
            reverse("traditions:occasion-edit", args=[occasion.pk]),
            {"start_date": "2031-06-01", "end_date": "2031-06-03"},
        )
        self.assertRedirects(response, reverse("traditions:calendar"))
        occasion.refresh_from_db()
        self.assertEqual(occasion.start_date, date(2031, 6, 1))


class CalendarPermissionTests(WorshipLeaderTestCase):
    def test_non_administrators_cannot_edit_dates(self):
        season = Season.objects.first()
        response = self.client.post(
            reverse("traditions:season-edit", args=[season.pk]),
            {"start_date": "2031-01-01", "end_date": "2031-01-02"},
        )
        self.assertEqual(response.status_code, 403)


class PlanSeasonTests(WorshipLeaderTestCase):
    def make_plan(self, day):
        return WorshipPlan.objects.create(
            title="Sunday service",
            service_datetime=timezone.make_aware(
                datetime.combine(day, datetime.min.time().replace(hour=9))
            ),
            service_theme=Theme.objects.filter(tradition=None).first(),
        )

    def test_plan_detail_shows_the_derived_season(self):
        activate("roman-catholic")
        plan = self.make_plan(date(2027, 3, 7))
        response = self.client.get(
            reverse("worship:plan-detail", args=[plan.public_id])
        )
        self.assertContains(response, "Lent")

    def test_plan_list_shows_the_derived_season(self):
        activate("roman-catholic")
        self.make_plan(date(2026, 12, 6))
        response = self.client.get(reverse("worship:plan-list") + "?timing=all")
        self.assertContains(response, "Season: <strong>Advent</strong>", html=False)

    def test_inc_plan_shows_no_season(self):
        activate("iglesia-ni-cristo")
        plan = self.make_plan(date(2027, 3, 7))
        response = self.client.get(
            reverse("worship:plan-detail", args=[plan.public_id])
        )
        self.assertNotContains(response, "Season</dt>")
