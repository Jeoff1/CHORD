from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, UserRole
from apps.traditions import services
from apps.traditions.models import Tradition

PASSWORD = "Correct-Horse-47-Battery"


def make_user(username, *role_codes):
    user = get_user_model().objects.create_user(username, password=PASSWORD)
    for code in role_codes:
        UserRole.objects.create(user=user, role=Role.objects.get(code=code))
    return user


def activate_tradition(tradition_code):
    profile = services.get_church_profile()
    profile.tradition = Tradition.objects.get(code=tradition_code)
    profile.save()


def reload_user(user):
    return get_user_model().objects.get(pk=user.pk)


class TraditionRoleAccessTests(TestCase):
    def test_active_tradition_role_grants_its_permissions(self):
        activate_tradition("alliance")
        pastor = make_user("pastor", "alliance_senior_pastor")

        self.assertTrue(pastor.has_perm("accounts.manage_accounts"))

    def test_inactive_tradition_role_grants_no_access(self):
        activate_tradition("alliance")
        priest = make_user("priest", "rc_parish_priest")

        self.assertFalse(priest.has_perm("accounts.manage_accounts"))
        self.assertFalse(priest.has_perm("events.view_event"))
        self.assertFalse(priest.has_role("rc_parish_priest"))

    def test_switching_tradition_moves_access_between_preset_roles(self):
        activate_tradition("alliance")
        minister = make_user("minister", "inc_minister")
        self.assertFalse(minister.has_perm("accounts.manage_accounts"))

        activate_tradition("iglesia-ni-cristo")

        self.assertTrue(reload_user(minister).has_perm("accounts.manage_accounts"))

    def test_common_roles_work_under_every_tradition(self):
        for code in ("alliance", "roman-catholic", "iglesia-ni-cristo"):
            with self.subTest(tradition=code):
                activate_tradition(code)
                leader = reload_user(
                    make_user(f"leader-{code}", Role.Code.WORSHIP_LEADER)
                )
                self.assertTrue(leader.has_perm("worship.manage_worship_plans"))
                self.assertFalse(leader.has_perm("accounts.manage_accounts"))
                self.assertTrue(leader.has_role(Role.Code.WORSHIP_LEADER))


class TraditionRoleAssignmentTests(TestCase):
    url = reverse("accounts:user-add")

    def setUp(self):
        activate_tradition("alliance")
        self.client.force_login(make_user("admin", Role.Code.CHURCH_ADMINISTRATOR))

    def create_account(self, role_code):
        return self.client.post(
            self.url,
            {
                "username": "newcomer",
                "password1": PASSWORD,
                "password2": PASSWORD,
                "is_active": "on",
                "roles": [Role.objects.get(code=role_code).pk],
            },
        )

    def test_administrator_assigns_an_active_tradition_role(self):
        response = self.create_account("alliance_head_deacon")

        self.assertRedirects(response, reverse("accounts:user-list"))
        newcomer = get_user_model().objects.get(username="newcomer")
        self.assertTrue(newcomer.has_role("alliance_head_deacon"))
        self.assertTrue(newcomer.has_perm("ministries.manage_assigned_ministries"))

    def test_inactive_tradition_roles_are_not_offered(self):
        response = self.create_account("rc_parish_priest")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="newcomer").exists())
        self.assertNotContains(response, "Parish Priest")
