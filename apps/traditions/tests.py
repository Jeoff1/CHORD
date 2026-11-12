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
        self.client.force_login(make_user("admin", "church_administrator"))

        response = self.client.post(
            self.url,
            {"name": "St. Joseph Parish", "tradition": tradition("roman-catholic").pk},
        )

        self.assertRedirects(response, self.url)
        self.assertEqual(services.get_active_tradition().name, "Roman Catholic")
        self.assertEqual(services.get_church_profile().name, "St. Joseph Parish")

    def test_switching_tradition_keeps_existing_data(self):
        Fund.objects.create(name="Building Fund")
        member = make_user("member", "church_member")
        self.client.force_login(make_user("admin", "church_administrator"))

        self.client.post(
            self.url,
            {"name": "My Church", "tradition": tradition("iglesia-ni-cristo").pk},
        )

        self.assertTrue(Fund.objects.filter(name="Building Fund").exists())
        self.assertTrue(member.roles.filter(code="church_member").exists())

    def test_non_administrator_cannot_change_profile(self):
        self.client.force_login(make_user("member", "church_member"))
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
        self.client.force_login(make_user("member", "church_member"))
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertContains(response, "My Church")
        self.assertContains(response, "Alliance")

    def test_only_administrators_see_church_profile_link(self):
        link = reverse("traditions:church-profile")
        self.client.force_login(make_user("member", "church_member"))
        self.assertNotContains(self.client.get(reverse("accounts:dashboard")), link)

        self.client.force_login(make_user("admin", "church_administrator"))
        self.assertContains(self.client.get(reverse("accounts:dashboard")), link)


class TerminologyServiceTests(TestCase):
    def use_tradition(self, code):
        profile = services.get_church_profile()
        profile.tradition = tradition(code)
        profile.save()

    def test_service_term_follows_the_active_tradition(self):
        self.assertEqual(services.term("service"), "Worship Service")
        self.use_tradition("roman-catholic")
        self.assertEqual(services.term("service"), "Mass")
        self.use_tradition("iglesia-ni-cristo")
        self.assertEqual(services.term("service"), "Pagsamba")

    def test_unknown_term_is_an_error(self):
        with self.assertRaises(KeyError):
            services.term("not-a-term")


class ModuleToggleServiceTests(TestCase):
    def test_presets_enable_every_module_by_default(self):
        self.assertEqual(
            services.enabled_modules(),
            {"members", "ministries", "events", "giving", "worship"},
        )

    def test_override_disables_a_module_and_survives_tradition_switch(self):
        services.set_module_enabled("giving", False)
        self.assertNotIn("giving", services.enabled_modules())

        profile = services.get_church_profile()
        profile.tradition = tradition("roman-catholic")
        profile.save()
        self.assertNotIn("giving", services.enabled_modules())
        self.assertFalse(services.is_module_enabled("giving"))
        self.assertTrue(services.is_module_enabled("members"))


class ModuleGatingHttpTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin", "church_administrator")
        self.client.force_login(self.admin)

    def test_disabled_module_url_returns_404_and_link_disappears(self):
        giving_url = reverse("giving:contribution-list")
        self.assertEqual(self.client.get(giving_url).status_code, 200)
        self.assertContains(self.client.get(reverse("accounts:dashboard")), giving_url)

        services.set_module_enabled("giving", False)

        self.assertEqual(self.client.get(giving_url).status_code, 404)
        self.assertEqual(self.client.post(giving_url).status_code, 404)
        self.assertNotContains(
            self.client.get(reverse("accounts:dashboard")), giving_url
        )

    def test_disabled_module_hides_shell_links_and_dashboard_actions(self):
        dashboard = reverse("accounts:dashboard")
        for url in (reverse("worship:choir-activity"), reverse("worship:plan-add")):
            self.assertContains(self.client.get(dashboard), url)

        services.set_module_enabled("worship", False)

        response = self.client.get(dashboard)
        for url in (reverse("worship:choir-activity"), reverse("worship:plan-add")):
            self.assertNotContains(response, url)

    def test_reenabling_a_module_restores_it(self):
        services.set_module_enabled("members", False)
        services.set_module_enabled("members", True)
        self.assertEqual(self.client.get(reverse("members:list")).status_code, 200)

    def test_permissions_stay_authoritative_for_enabled_modules(self):
        self.client.force_login(make_user("member", "church_member"))
        self.assertEqual(
            self.client.get(reverse("giving:contribution-list")).status_code, 403
        )

    def test_core_pages_are_never_gated(self):
        for code in services.MODULES:
            services.set_module_enabled(code, False)
        self.assertEqual(
            self.client.get(reverse("accounts:dashboard")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("traditions:church-profile")).status_code, 200
        )

    def test_administrator_toggles_a_module_on_the_church_profile(self):
        url = reverse("traditions:church-profile")
        enabled = sorted(set(services.MODULES) - {"worship"})
        response = self.client.post(
            url,
            {
                "name": "My Church",
                "tradition": tradition("alliance").pk,
                "enabled_modules": enabled,
            },
        )
        self.assertRedirects(response, url)
        self.assertEqual(self.client.get(reverse("worship:song-list")).status_code, 404)
        self.assertNotContains(
            self.client.get(reverse("accounts:dashboard")), reverse("worship:song-list")
        )


class TerminologyHttpTests(TestCase):
    def test_switching_tradition_changes_navigation_and_headings(self):
        self.client.force_login(make_user("admin", "church_administrator"))
        plans = reverse("worship:plan-list")
        self.assertContains(self.client.get(plans), "Worship Service plans")

        self.client.post(
            reverse("traditions:church-profile"),
            {
                "name": "St. Joseph Parish",
                "tradition": tradition("roman-catholic").pk,
                "enabled_modules": list(services.MODULES),
            },
        )

        response = self.client.get(plans)
        self.assertContains(response, "<h1>Mass plans</h1>", html=False)
        self.assertNotContains(response, "Worship Service plans")
