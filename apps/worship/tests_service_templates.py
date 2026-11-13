from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from apps.traditions.models import ServiceTemplate, SongSlot, Theme, Tradition
from apps.traditions.services import available_service_templates

from .models import PlanSong, WorshipPlan
from .services import add_plan_song, move_plan_song
from .tests_songbooks import WorshipLeaderTestCase, activate, song_in


def when(days=3):
    return timezone.now() + timedelta(days=days)


class PresetServiceTemplateTests(WorshipLeaderTestCase):
    def test_each_preset_has_templates_with_ordered_slots(self):
        for tradition in Tradition.objects.all():
            with self.subTest(tradition=tradition.code):
                templates = tradition.service_templates.all()
                self.assertTrue(templates.exists())
                for template in templates:
                    positions = list(template.slots.values_list("position", flat=True))
                    self.assertTrue(positions)
                    self.assertEqual(positions, sorted(positions))

    def test_mass_has_the_liturgical_slots_in_order(self):
        mass = ServiceTemplate.objects.get(
            tradition__code="roman-catholic", code="mass"
        )
        self.assertEqual(
            [slot.name for slot in mass.slots.all()],
            ["Entrance", "Offertory", "Communion", "Recessional"],
        )

    def test_only_the_active_traditions_templates_are_available(self):
        activate("alliance")
        self.assertEqual(
            {t.tradition.code for t in available_service_templates()}, {"alliance"}
        )


class PlanFromTemplateTests(WorshipLeaderTestCase):
    def setUp(self):
        super().setUp()
        activate("roman-catholic")
        self.mass = ServiceTemplate.objects.get(code="mass")
        self.grace = Theme.objects.get(code="grace", tradition=None)

    def plan_data(self, **extra):
        data = {
            "title": "Sunday Mass",
            "service_datetime": when().strftime("%Y-%m-%dT%H:%M"),
            "status": WorshipPlan.Status.DRAFT,
            "service_theme": self.grace.pk,
        }
        data.update(extra)
        return data

    def test_plan_created_from_a_template_shows_its_open_slots(self):
        self.client.post(
            reverse("worship:plan-add"), self.plan_data(service_template=self.mass.pk)
        )
        plan = WorshipPlan.objects.get()
        self.assertEqual(plan.service_template, self.mass)
        outline = plan.slot_outline()
        self.assertEqual(
            [slot.name for slot, _ in outline],
            ["Entrance", "Offertory", "Communion", "Recessional"],
        )
        self.assertTrue(all(items == [] for _, items in outline))
        response = self.client.get(
            reverse("worship:plan-detail", args=(plan.public_id,))
        )
        self.assertContains(response, "Offertory")

    def test_plan_without_a_template_still_works(self):
        self.client.post(reverse("worship:plan-add"), self.plan_data())
        plan = WorshipPlan.objects.get()
        self.assertIsNone(plan.service_template)
        self.assertEqual(plan.slot_outline(), [])
        song = song_in("general", "Amazing Grace")
        url = reverse("worship:plan-song-add", args=(plan.public_id,))
        self.client.post(url, {"song": song.pk})
        self.assertIsNone(plan.setlist_items.get().song_slot)
        response = self.client.get(
            reverse("worship:plan-detail", args=(plan.public_id,))
        )
        self.assertEqual(response.status_code, 200)

    def test_a_template_from_another_tradition_is_refused(self):
        other = ServiceTemplate.objects.exclude(
            tradition__code="roman-catholic"
        ).first()
        response = self.client.post(
            reverse("worship:plan-add"), self.plan_data(service_template=other.pk)
        )
        self.assertIn("service_template", response.context["form"].errors)


class SongSlotSetlistTests(WorshipLeaderTestCase):
    def setUp(self):
        super().setUp()
        activate("roman-catholic")
        self.mass = ServiceTemplate.objects.get(code="mass")
        self.plan = WorshipPlan.objects.create(
            title="Mass", service_datetime=when(), service_template=self.mass
        )
        self.url = reverse("worship:plan-song-add", args=(self.plan.public_id,))
        self.entrance = self.mass.slots.get(name="Entrance")
        self.communion = self.mass.slots.get(name="Communion")

    def test_adding_a_song_fills_the_chosen_slot(self):
        song = song_in("general", "Gathering Hymn")
        self.client.post(self.url, {"song": song.pk, "song_slot": self.entrance.pk})
        item = self.plan.setlist_items.get()
        self.assertEqual(item.song_slot, self.entrance)
        self.assertEqual(dict(self.plan.slot_outline())[self.entrance], [item])

    def test_a_slot_from_another_template_is_refused(self):
        foreign = SongSlot.objects.exclude(template=self.mass).first()
        song = song_in("general", "Gathering Hymn")
        response = self.client.post(
            self.url, {"song": song.pk, "song_slot": foreign.pk}
        )
        self.assertIn("song_slot", response.context["form"].errors)
        self.assertFalse(self.plan.setlist_items.exists())

    def test_position_stays_authoritative_over_slot_order(self):
        first = add_plan_song(
            plan=self.plan, song=song_in("general", "A"), song_slot=self.communion
        )
        second = add_plan_song(
            plan=self.plan, song=song_in("general", "B"), song_slot=self.entrance
        )
        self.assertEqual([first, second], list(self.plan.setlist_items.all()))
        move_plan_song(plan_song=second, direction="up")
        second.refresh_from_db()
        self.assertEqual(second.position, 1)
        self.assertEqual(second.song_slot, self.entrance)
        self.assertEqual(list(PlanSong.objects.filter(plan=self.plan)), [second, first])

    def test_a_slot_from_another_template_fails_model_validation(self):
        from django.core.exceptions import ValidationError

        foreign = SongSlot.objects.exclude(template=self.mass).first()
        item = PlanSong(
            plan=self.plan, song=song_in("general", "X"), position=1, song_slot=foreign
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_changing_the_template_clears_stale_slots(self):
        item = add_plan_song(
            plan=self.plan, song=song_in("general", "A"), song_slot=self.entrance
        )
        self.client.post(
            reverse("worship:plan-edit", args=(self.plan.public_id,)),
            {
                "title": "Mass",
                "service_datetime": when().strftime("%Y-%m-%dT%H:%M"),
                "status": WorshipPlan.Status.DRAFT,
                "service_theme": Theme.objects.get(code="grace", tradition=None).pk,
            },
        )
        item.refresh_from_db()
        self.assertIsNone(item.song_slot)
        self.assertTrue(PlanSong.objects.filter(pk=item.pk).exists())
