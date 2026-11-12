from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, UserRole
from apps.giving.models import Fund

from . import services

PASSWORD = "Correct-Horse-47-Battery"


def make_user(username, role_code=None):
    user = get_user_model().objects.create_user(username, password=PASSWORD)
    if role_code:
        UserRole.objects.create(user=user, role=Role.objects.get(code=role_code))
    return user


def tradition(code):
    return next(t for t in services.list_traditions() if t.code == code)


class TraditionConfigServiceTests(TestCase):
    def test_three_tradition_presets_are_available(self):
        self.assertEqual(
            [t.name for t in services.list_traditions()],
            ["Alliance", "Iglesia Ni Cristo", "Roman Catholic"],
        )

    def test_active_tradition_defaults_to_alliance(self):
        self.assertEqual(services.get_active_tradition().name, "Alliance")
        self.assertEqual(services.get_church_profile().name, "My Church")

    def test_active_tradition_follows_the_church_profile(self):
        profile = services.get_church_profile()
        profile.tradition = tradition("iglesia-ni-cristo")
        profile.save()
        self.assertEqual(services.get_active_tradition().name, "Iglesia Ni Cristo")


class ChurchProfileViewTests(TestCase):
    url = reverse("traditions:church-profile")

    def test_administrator_switches_tradition_and_name(self):
        self.client.force_login(make_user("admin", Role.Code.CHURCH_ADMINISTRATOR))

        response = self.client.post(
            self.url,
            {"name": "St. Joseph Parish", "tradition": tradition("roman-catholic").pk},
        )

        self.assertRedirects(response, self.url)
        self.assertEqual(services.get_active_tradition().name, "Roman Catholic")
        self.assertEqual(services.get_church_profile().name, "St. Joseph Parish")

    def test_switching_tradition_keeps_existing_data(self):
        Fund.objects.create(name="Building Fund")
        member = make_user("member", Role.Code.CHURCH_MEMBER)
        self.client.force_login(make_user("admin", Role.Code.CHURCH_ADMINISTRATOR))

        self.client.post(
            self.url,
            {"name": "My Church", "tradition": tradition("iglesia-ni-cristo").pk},
        )

        self.assertTrue(Fund.objects.filter(name="Building Fund").exists())
        self.assertTrue(member.roles.filter(code=Role.Code.CHURCH_MEMBER).exists())

    def test_non_administrator_cannot_change_profile(self):
        self.client.force_login(make_user("member", Role.Code.CHURCH_MEMBER))
        self.assertEqual(self.client.get(self.url).status_code, 403)
        response = self.client.post(
            self.url, {"name": "Hijacked", "tradition": tradition("roman-catholic").pk}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(services.get_active_tradition().name, "Alliance")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])


class ApplicationShellTraditionTests(TestCase):
    def test_shell_shows_active_church_and_tradition(self):
        self.client.force_login(make_user("member", Role.Code.CHURCH_MEMBER))
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertContains(response, "My Church")
        self.assertContains(response, "Alliance")

    def test_only_administrators_see_church_profile_link(self):
        link = reverse("traditions:church-profile")
        self.client.force_login(make_user("member", Role.Code.CHURCH_MEMBER))
        self.assertNotContains(self.client.get(reverse("accounts:dashboard")), link)

        self.client.force_login(make_user("admin", Role.Code.CHURCH_ADMINISTRATOR))
        self.assertContains(self.client.get(reverse("accounts:dashboard")), link)
