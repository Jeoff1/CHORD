from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, UserRole
from apps.members.models import Member
from apps.traditions import services
from apps.worship.tests_songbooks import PASSWORD, activate

from .models import ChurchRecord, ChurchRecordType


def login_as(client, role_code, username=None):
    user = get_user_model().objects.create_user(
        username or role_code, password=PASSWORD
    )
    UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    client.force_login(user)
    return user


def record_type(name, tradition="alliance"):
    return ChurchRecordType.objects.get(tradition__code=tradition, name=name)


class ConfidentialityTests(TestCase):
    def setUp(self):
        activate("alliance")
        self.record = ChurchRecord.objects.create(
            record_type=record_type("Baptism"),
            name="Ana Cruz",
            date=date(2026, 5, 3),
        )

    def test_unauthorized_roles_cannot_see_records(self):
        for role in ("church_member", "worship_leader", "ministry_leader"):
            with self.subTest(role=role):
                login_as(self.client, role, username=f"u-{role}")
                for url in (
                    reverse("records:list"),
                    reverse("records:detail", args=[self.record.public_id]),
                    reverse("records:add"),
                    reverse("records:edit", args=[self.record.public_id]),
                ):
                    self.assertEqual(self.client.get(url).status_code, 403)

    def test_church_administrator_sees_records(self):
        login_as(self.client, "church_administrator")
        self.assertContains(self.client.get(reverse("records:list")), "Ana Cruz")

    def test_tradition_admin_role_sees_records(self):
        login_as(self.client, "alliance_senior_pastor")
        self.assertContains(self.client.get(reverse("records:list")), "Ana Cruz")

    def test_anonymous_users_are_sent_to_login(self):
        response = self.client.get(reverse("records:list"))
        self.assertEqual(response.status_code, 302)


class RecordTypesByTraditionTests(TestCase):
    def names(self, code):
        return set(
            ChurchRecordType.objects.filter(tradition__code=code).values_list(
                "name", flat=True
            )
        )

    def test_presets_ship_their_own_record_types(self):
        self.assertIn("Confirmation", self.names("roman-catholic"))
        self.assertIn("Baby Dedication", self.names("alliance"))
        self.assertNotIn("Confirmation", self.names("iglesia-ni-cristo"))

    def test_form_offers_only_the_active_traditions_types(self):
        activate("roman-catholic")
        login_as(self.client, "church_administrator")
        response = self.client.get(reverse("records:add"))
        self.assertContains(response, "Confirmation")
        self.assertNotContains(response, "Baby Dedication")


class CrudAndAuditTests(TestCase):
    def setUp(self):
        activate("alliance")
        self.admin = login_as(self.client, "church_administrator")
        self.member = Member.objects.create(first_name="Ben", last_name="Reyes")

    def form_data(self, **overrides):
        return {
            "record_type": record_type("Baptism").pk,
            "member": self.member.pk,
            "name": "",
            "officiant": "Ptr. Santos",
            "place": "Main sanctuary",
            "date": "2026-04-05",
            "notes": "",
            **overrides,
        }

    def create(self, **overrides):
        return self.client.post(reverse("records:add"), self.form_data(**overrides))

    def test_create_with_member_records_audit_event(self):
        response = self.create()
        record = ChurchRecord.objects.get()
        self.assertRedirects(
            response, reverse("records:detail", args=[record.public_id])
        )
        self.assertEqual(record.member, self.member)
        detail = self.client.get(response.url)
        self.assertContains(detail, "Ben Reyes")
        self.assertContains(detail, "Created")
        self.assertContains(detail, self.admin.username)

    def test_create_with_free_text_name(self):
        self.create(member="", name="Visitor Child")
        self.assertEqual(ChurchRecord.objects.get().display_name, "Visitor Child")

    def test_member_or_name_is_required(self):
        response = self.create(member="", name="")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChurchRecord.objects.exists())
        self.assertContains(response, "Link a member or enter a name.")

    def test_rejects_another_traditions_record_type(self):
        self.create(record_type=record_type("Confirmation", "roman-catholic").pk)
        self.assertFalse(ChurchRecord.objects.exists())

    def test_edit_records_updated_audit_with_field_names_only(self):
        self.create()
        record = ChurchRecord.objects.get()
        url = reverse("records:edit", args=[record.public_id])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, self.form_data(officiant="Ptr. Lim"))
        self.assertRedirects(
            response, reverse("records:detail", args=[record.public_id])
        )
        record.refresh_from_db()
        self.assertEqual(record.officiant, "Ptr. Lim")
        detail = self.client.get(response.url)
        self.assertContains(detail, "Updated")
        self.assertContains(detail, "officiant")
        self.assertNotContains(detail, "Ptr. Santos")  # old values never logged

    def test_edit_keeps_a_type_from_a_previous_tradition(self):
        self.create()
        record = ChurchRecord.objects.get()
        activate("roman-catholic")
        response = self.client.post(
            reverse("records:edit", args=[record.public_id]),
            self.form_data(notes="After the switch"),
        )
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.notes, "After the switch")


class SearchAndFilterTests(TestCase):
    def setUp(self):
        activate("alliance")
        login_as(self.client, "church_administrator")
        ChurchRecord.objects.create(
            record_type=record_type("Baptism"), name="Ana Cruz", date=date(2026, 1, 10)
        )
        ChurchRecord.objects.create(
            record_type=record_type("Marriage"),
            name="Carlo Dizon",
            date=date(2026, 6, 20),
        )
        member = Member.objects.create(first_name="Dina", last_name="Ong")
        ChurchRecord.objects.create(
            record_type=record_type("Funeral"), member=member, date=date(2026, 9, 1)
        )

    def get(self, **params):
        return self.client.get(reverse("records:list"), params)

    def test_search_by_free_text_and_member_name(self):
        response = self.get(q="ana")
        self.assertContains(response, "Ana Cruz")
        self.assertNotContains(response, "Carlo Dizon")
        self.assertContains(self.get(q="ong"), "Dina Ong")

    def test_filter_by_type(self):
        response = self.get(type=record_type("Marriage").pk)
        self.assertContains(response, "Carlo Dizon")
        self.assertNotContains(response, "Ana Cruz")

    def test_filter_by_date_range(self):
        response = self.get(date_from="2026-02-01", date_to="2026-08-31")
        self.assertContains(response, "Carlo Dizon")
        self.assertNotContains(response, "Ana Cruz")
        self.assertNotContains(response, "Dina Ong")


class ModuleToggleTests(TestCase):
    def test_disabled_module_is_hidden(self):
        activate("alliance")
        login_as(self.client, "church_administrator")
        self.assertContains(
            self.client.get(reverse("accounts:dashboard")), reverse("records:list")
        )
        services.set_module_enabled("records", False)
        self.assertEqual(self.client.get(reverse("records:list")).status_code, 404)
        self.assertNotContains(
            self.client.get(reverse("accounts:dashboard")), reverse("records:list")
        )

    def test_enabled_by_default_for_every_preset(self):
        for code in ("alliance", "roman-catholic", "iglesia-ni-cristo"):
            with self.subTest(tradition=code):
                activate(code)
                self.assertTrue(services.is_module_enabled("records"))
