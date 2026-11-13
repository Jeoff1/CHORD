from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.traditions.models import Theme

from .models import WorshipPlan
from .tests_songbooks import WorshipLeaderTestCase, activate


def when(days=3):
    return timezone.now() + timedelta(days=days)


class ServiceThemeTests(WorshipLeaderTestCase):
    def setUp(self):
        super().setUp()
        activate("alliance")
        self.grace = Theme.objects.get(code="grace", tradition=None)

    def plan_data(self, **extra):
        data = {
            "title": "Sunday Service",
            "service_datetime": when().strftime("%Y-%m-%dT%H:%M"),
            "status": WorshipPlan.Status.DRAFT,
        }
        data.update(extra)
        return data

    def test_new_plan_requires_a_service_theme(self):
        response = self.client.post(reverse("worship:plan-add"), self.plan_data())
        self.assertIn("service_theme", response.context["form"].errors)
        self.assertFalse(WorshipPlan.objects.exists())

    def test_new_plan_saves_theme_sermon_and_scripture(self):
        self.client.post(
            reverse("worship:plan-add"),
            self.plan_data(
                service_theme=self.grace.pk,
                sermon_title="Amazing Grace",
                scripture_reference="Ephesians 2:8-9",
            ),
        )
        plan = WorshipPlan.objects.get()
        self.assertEqual(plan.service_theme, self.grace)
        self.assertEqual(plan.sermon_title, "Amazing Grace")
        self.assertEqual(plan.scripture_reference, "Ephesians 2:8-9")

    def test_theme_from_another_tradition_is_refused(self):
        eucharist = Theme.objects.get(code="eucharist")
        response = self.client.post(
            reverse("worship:plan-add"), self.plan_data(service_theme=eucharist.pk)
        )
        self.assertIn("service_theme", response.context["form"].errors)
        self.assertFalse(WorshipPlan.objects.exists())

    def test_existing_plan_without_theme_can_still_be_edited(self):
        plan = WorshipPlan.objects.create(title="Old", service_datetime=when())
        self.client.post(
            reverse("worship:plan-edit", args=(plan.public_id,)),
            self.plan_data(title="Old renamed"),
        )
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Old renamed")
        self.assertIsNone(plan.service_theme)

    def test_themed_plan_cannot_drop_its_theme(self):
        plan = WorshipPlan.objects.create(
            title="Themed", service_datetime=when(), service_theme=self.grace
        )
        response = self.client.post(
            reverse("worship:plan-edit", args=(plan.public_id,)), self.plan_data()
        )
        self.assertIn("service_theme", response.context["form"].errors)

    def test_plan_keeps_a_theme_no_longer_on_offer(self):
        eucharist = Theme.objects.get(code="eucharist")
        plan = WorshipPlan.objects.create(
            title="Themed", service_datetime=when(), service_theme=eucharist
        )
        self.client.post(
            reverse("worship:plan-edit", args=(plan.public_id,)),
            self.plan_data(title="Renamed", service_theme=eucharist.pk),
        )
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Renamed")
        self.assertEqual(plan.service_theme, eucharist)

    def test_theme_is_shown_on_list_and_detail(self):
        plan = WorshipPlan.objects.create(
            title="Themed",
            service_datetime=when(),
            service_theme=self.grace,
            sermon_title="Saved by Grace",
            scripture_reference="Titus 3:5",
        )
        listing = self.client.get(reverse("worship:plan-list"))
        self.assertContains(listing, self.grace.name)
        detail = self.client.get(reverse("worship:plan-detail", args=(plan.public_id,)))
        self.assertContains(detail, self.grace.name)
        self.assertContains(detail, "Saved by Grace")
        self.assertContains(detail, "Titus 3:5")


class ServiceThemeModelRuleTests(TestCase):
    def test_new_plan_without_theme_fails_validation(self):
        plan = WorshipPlan(title="New", service_datetime=when())
        with self.assertRaises(ValidationError) as caught:
            plan.full_clean(exclude=["created_by"])
        self.assertIn("service_theme", caught.exception.message_dict)

    def test_existing_unthemed_plan_still_validates(self):
        plan = WorshipPlan.objects.create(title="Old", service_datetime=when())
        plan.full_clean(exclude=["created_by"])

    def test_admin_refuses_new_plan_without_theme(self):
        admin = get_user_model().objects.create_superuser("root", password="x")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("admin:worship_worshipplan_add"),
            {
                "title": "Admin plan",
                "service_datetime_0": when().strftime("%Y-%m-%d"),
                "service_datetime_1": "10:00:00",
                "status": WorshipPlan.Status.DRAFT,
                "created_by": admin.pk,
                "setlist_items-TOTAL_FORMS": "0",
                "setlist_items-INITIAL_FORMS": "0",
                "choir_participations-TOTAL_FORMS": "0",
                "choir_participations-INITIAL_FORMS": "0",
            },
        )
        self.assertIn("service_theme", response.context["adminform"].form.errors)
        self.assertFalse(WorshipPlan.objects.exists())
