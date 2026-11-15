from datetime import date, datetime

from django.utils import timezone

from apps.traditions import services
from apps.traditions.models import ServiceTemplate, Theme
from apps.worship.models import WorshipPlan
from apps.worship.tests_songbooks import WorshipLeaderTestCase, activate


def mass_plan(day):
    return WorshipPlan.objects.create(
        title="Sunday Mass",
        service_datetime=timezone.make_aware(
            datetime.combine(day, datetime.min.time().replace(hour=9))
        ),
        service_theme=Theme.objects.filter(tradition=None).first(),
        service_template=ServiceTemplate.objects.get(
            tradition__code="roman-catholic", code="mass"
        ),
    )


class SlotContextTests(WorshipLeaderTestCase):
    def test_returns_theme_season_songbooks_and_slot_in_one_call(self):
        activate("roman-catholic")
        plan = mass_plan(date(2027, 3, 7))
        slot = plan.service_template.slots.get(name="Communion")

        context = services.slot_context(plan, slot)

        self.assertEqual(context.service_theme, plan.service_theme)
        self.assertEqual(context.season.name, "Lent")
        self.assertEqual(set(context.songbooks), set(services.allowed_songbooks()))
        self.assertEqual(context.song_slot, slot)

    def test_season_is_none_outside_every_season(self):
        activate("roman-catholic")
        plan = mass_plan(date(1990, 1, 1))
        context = services.slot_context(plan, plan.service_template.slots.first())
        self.assertIsNone(context.season)

    def test_rejects_a_slot_from_another_template(self):
        activate("roman-catholic")
        plan = mass_plan(date(2027, 3, 7))
        other = (
            ServiceTemplate.objects.exclude(pk=plan.service_template_id)
            .first()
            .slots.first()
        )
        with self.assertRaises(ValueError):
            services.slot_context(plan, other)
