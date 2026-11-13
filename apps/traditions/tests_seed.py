from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.members.models import Member
from apps.records.models import ChurchRecord
from apps.traditions import services
from apps.worship.models import PlanSong, Song, SongResource, WorshipPlan

from .demo import DEMO_CHURCHES, DEMO_EMAIL_DOMAIN

TRADITIONS = ("roman-catholic", "alliance", "iglesia-ni-cristo")
MODELS = (
    get_user_model(),
    UserRole,
    Member,
    Song,
    Song.themes.through,
    WorshipPlan,
    PlanSong,
    ChurchRecord,
)


def seed(code, *args):
    call_command("seed_tradition", code, *args, stdout=StringIO())


def counts():
    return {model.__name__: model.objects.count() for model in MODELS}


class SeedTraditionTests(TestCase):
    def test_each_tradition_seeds_a_complete_church(self):
        for code in TRADITIONS:
            with self.subTest(tradition=code):
                seed(code)
                profile = services.get_church_profile()
                self.assertEqual(profile.tradition.code, code)
                self.assertEqual(profile.name, DEMO_CHURCHES[code]["church_name"])
                demo = DEMO_CHURCHES[code]
                users = get_user_model().objects.filter(
                    username__in=[u["username"] for u in demo["users"]]
                )
                self.assertEqual(users.count(), len(demo["users"]))
                for user in users:
                    self.assertTrue(user.roles.exists())
                    self.assertTrue(
                        set(user.roles.all()) <= set(services.roles_in_effect())
                    )
                plans = WorshipPlan.objects.filter(
                    title__in=[p["title"] for p in demo["plans"]]
                )
                self.assertEqual(plans.count(), len(demo["plans"]))
                allowed = set(services.allowed_songbooks())
                for plan in plans:
                    self.assertIsNotNone(plan.service_theme)
                    self.assertEqual(plan.service_template.tradition.code, code)
                    for item in plan.setlist_items.all():
                        self.assertIn(item.song.songbook, allowed)
                        self.assertEqual(
                            item.song_slot.template_id, plan.service_template_id
                        )
                self.assertTrue(
                    ChurchRecord.objects.filter(
                        record_type__tradition__code=code
                    ).exists()
                )
                self.assertTrue(
                    Song.objects.filter(songbook__in=allowed, themes__isnull=False)
                    .distinct()
                    .exists()
                )

    def test_running_twice_creates_no_duplicates(self):
        for code in TRADITIONS:
            with self.subTest(tradition=code):
                seed(code)
                before = counts()
                seed(code)
                self.assertEqual(counts(), before)

    def test_metadata_only_songbooks_hold_no_lyrics_or_sheets(self):
        for code in TRADITIONS:
            seed(code)
        metadata_only = Song.objects.filter(songbook__metadata_only=True)
        self.assertTrue(metadata_only.exists())
        self.assertFalse(SongResource.objects.filter(song__in=metadata_only).exists())
        self.assertFalse(metadata_only.exclude(notes="").exists())

    def test_seed_data_has_no_secrets_or_real_personal_data(self):
        seed("alliance")
        for user in get_user_model().objects.all():
            self.assertFalse(user.has_usable_password())
            self.assertTrue(user.email.endswith(f"@{DEMO_EMAIL_DOMAIN}"))
        for member in Member.objects.all():
            self.assertTrue(
                member.email == "" or member.email.endswith(f"@{DEMO_EMAIL_DOMAIN}")
            )
            self.assertIsNone(member.date_of_birth)
            self.assertEqual(member.address, "")
            self.assertEqual(member.phone_number, "")

    def test_password_option_sets_a_shared_demo_password(self):
        seed("alliance", "--password", "Demo-Only-Pass-91")
        user = get_user_model().objects.get(
            username=DEMO_CHURCHES["alliance"]["users"][0]["username"]
        )
        self.assertTrue(user.check_password("Demo-Only-Pass-91"))

    def test_unknown_tradition_is_rejected(self):
        with self.assertRaises(CommandError):
            seed("lutheran")

    def test_switching_traditions_and_back_creates_no_duplicates(self):
        for code in TRADITIONS:
            seed(code)
        before = counts()
        for code in TRADITIONS:
            seed(code)
        self.assertEqual(counts(), before)


class SeedGuardTests(TestCase):
    def test_refuses_a_database_with_a_real_church_profile(self):
        profile = services.get_church_profile()
        profile.name = "Grace Community Church"
        profile.save()
        with self.assertRaisesMessage(CommandError, "Grace Community Church"):
            seed("alliance")
        self.assertEqual(services.get_church_profile().name, "Grace Community Church")
        self.assertFalse(WorshipPlan.objects.exists())

    def test_refuses_a_database_with_real_members(self):
        Member.objects.create(first_name="Real", last_name="Person")
        with self.assertRaisesMessage(CommandError, "1 member"):
            seed("alliance")
        self.assertEqual(Member.objects.count(), 1)

    def test_force_seeds_anyway(self):
        Member.objects.create(first_name="Real", last_name="Person")
        seed("alliance", "--force")
        self.assertEqual(
            services.get_church_profile().name,
            DEMO_CHURCHES["alliance"]["church_name"],
        )

    def test_reseeding_a_demo_database_needs_no_force(self):
        seed("roman-catholic")
        seed("alliance")
        self.assertEqual(services.get_active_tradition().code, "alliance")
