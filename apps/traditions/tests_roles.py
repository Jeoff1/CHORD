from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, UserRole
from apps.members.models import Member

from . import services
from .models import Tradition

PASSWORD = "Correct-Horse-47-Battery"
TRADITIONS = ("alliance", "iglesia-ni-cristo", "roman-catholic")


def activate_tradition(code):
    profile = services.get_church_profile()
    profile.tradition = Tradition.objects.get(code=code)
    profile.save()


def make_user(username, role):
    user = get_user_model().objects.create_user(username, password=PASSWORD)
    UserRole.objects.create(user=user, role=role)
    return user


class TraditionRoleAccessMatrixTests(TestCase):
    """Access follows the active Tradition's roles, under every Tradition."""

    def test_each_tradition_role_grants_exactly_its_catalogue_access(self):
        for active in TRADITIONS:
            with self.subTest(tradition=active):
                activate_tradition(active)
                for role in Role.objects.filter(tradition__isnull=False):
                    user = make_user(f"{active}-{role.code}", role)
                    self.client.force_login(user)
                    response = self.client.get(reverse("accounts:user-list"))

                    in_effect = role.tradition.code == active
                    grants_accounts = role.permissions.filter(
                        codename="manage_accounts"
                    ).exists()
                    expected = 200 if in_effect and grants_accounts else 403
                    self.assertEqual(response.status_code, expected, role.code)

    def test_every_role_grants_its_permissions_only_while_in_effect(self):
        roles = list(Role.objects.select_related("tradition"))
        users = {role.code: make_user(f"user-{role.code}", role) for role in roles}
        for active in TRADITIONS:
            activate_tradition(active)
            for role in roles:
                with self.subTest(tradition=active, role=role.code):
                    in_effect = role.tradition is None or role.tradition.code == active
                    granted = {
                        f"{p.content_type.app_label}.{p.codename}"
                        for p in role.permissions.select_related("content_type")
                    }
                    self.assertTrue(granted, "catalogue role grants nothing")
                    user = get_user_model().objects.get(pk=users[role.code].pk)
                    self.assertEqual(
                        user.get_all_permissions(), granted if in_effect else set()
                    )

    def test_every_tradition_has_an_administrator_role(self):
        for active in TRADITIONS:
            with self.subTest(tradition=active):
                activate_tradition(active)
                admin_roles = services.roles_in_effect().filter(
                    tradition__code=active,
                    permissions__codename="manage_accounts",
                )
                self.assertTrue(admin_roles.exists())


class UsersWithPermissionTests(TestCase):
    def test_finds_holders_through_in_effect_roles_only(self):
        activate_tradition("roman-catholic")
        priest = make_user("priest", Role.objects.get(code="rc_parish_priest"))
        make_user("pastor", Role.objects.get(code="alliance_senior_pastor"))
        choir = make_user("choir", Role.objects.get(code="choir_leader"))

        holders = services.users_with_permission("worship.manage_choir")

        self.assertCountEqual(holders, [priest, choir])


class ChoirLeadersListTests(TestCase):
    def test_roster_lists_choir_managers_of_the_active_tradition(self):
        activate_tradition("roman-catholic")
        priest = make_user("priest", Role.objects.get(code="rc_parish_priest"))
        Member.objects.create(
            first_name="Father",
            last_name="Santos",
            membership_status=Member.Status.MEMBER,
            user=priest,
        )
        self.client.force_login(priest)

        response = self.client.get(reverse("worship:choir-roster"))

        self.assertContains(response, "Father Santos")
