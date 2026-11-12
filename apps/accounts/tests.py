from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.staticfiles import finders
from django.db import IntegrityError, connection, transaction
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from .models import Profile, Role, UserRole
from .signals import synchronize_roles
from .views import UserListView

User = get_user_model()
PASSWORD = "Correct-Horse-47-Battery"


class SettingsTests(SimpleTestCase):
    def test_custom_user_model_and_postgresql_are_configured(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertEqual(User.__name__, "User")
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )


class DatabaseConnectionTests(TestCase):
    def test_database_connection(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            self.assertEqual(cursor.fetchone()[0], 1)


class RoleModelTests(TestCase):
    def test_all_six_roles_are_seeded_as_common_roles(self):
        self.assertSetEqual(
            set(
                Role.objects.filter(tradition__isnull=True).values_list(
                    "code", flat=True
                )
            ),
            set(Role.Code.values),
        )

    def test_user_can_have_multiple_unique_roles(self):
        user = User.objects.create_user("member", password=PASSWORD)
        choir_member = Role.objects.get(code=Role.Code.CHOIR_MEMBER)
        church_member = Role.objects.get(code=Role.Code.CHURCH_MEMBER)
        UserRole.objects.create(user=user, role=choir_member)
        UserRole.objects.create(user=user, role=church_member)

        self.assertSetEqual(
            set(user.roles.values_list("code", flat=True)),
            {Role.Code.CHOIR_MEMBER, Role.Code.CHURCH_MEMBER},
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            UserRole.objects.create(user=user, role=choir_member)

    def test_profile_is_created_with_account(self):
        user = User.objects.create_user("profile-user", password=PASSWORD)
        self.assertTrue(Profile.objects.filter(user=user).exists())


class RolePermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("administrator", password=PASSWORD)
        self.admin_role = Role.objects.get(code=Role.Code.CHURCH_ADMINISTRATOR)
        UserRole.objects.create(user=self.user, role=self.admin_role)

    def test_church_administrator_receives_account_permissions(self):
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.has_perm("accounts.manage_accounts"))
        self.assertTrue(user.has_perm("accounts.assign_roles"))
        self.assertTrue(user.has_perm("accounts.deactivate_accounts"))

    def test_church_administrator_is_not_superuser(self):
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.has_perm("auth.delete_permission"))

    def test_inactive_user_does_not_receive_role_permissions(self):
        self.user.is_active = False
        self.user.save(update_fields=("is_active",))
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.has_perm("accounts.manage_accounts"))

    def test_role_synchronization_removes_stale_administrator_permissions(self):
        stale_permission = Permission.objects.get(
            content_type__app_label="auth",
            codename="delete_permission",
        )
        self.admin_role.permissions.add(stale_permission)

        synchronize_roles(sender=None)

        self.assertFalse(
            self.admin_role.permissions.filter(pk=stale_permission.pk).exists()
        )


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("regular-user", password=PASSWORD)

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}",
        )

    def test_user_can_log_in_and_log_out_with_post(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": PASSWORD},
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_update_is_limited_to_logged_in_user(self):
        other = User.objects.create_user("other", password=PASSWORD)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:profile"),
            {"preferred_name": "Updated", "phone_number": "+63 900 000 0000"},
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.profile.refresh_from_db()
        other.profile.refresh_from_db()
        self.assertEqual(self.user.profile.preferred_name, "Updated")
        self.assertEqual(other.profile.preferred_name, "")

    def test_password_change_keeps_session_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": PASSWORD,
                "new_password1": "A-New-Secure-Password-52",
                "new_password2": "A-New-Secure-Password-52",
            },
        )
        self.assertRedirects(response, reverse("accounts:password-change-done"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_rejects_get_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_profile_update_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        response = csrf_client.post(
            reverse("accounts:profile"),
            {"preferred_name": "Blocked", "phone_number": "+63 900 000 0000"},
        )
        self.assertEqual(response.status_code, 403)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.preferred_name, "")

    def test_profile_rejects_invalid_phone_number(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:profile"),
            {"preferred_name": "Valid", "phone_number": "not-a-phone"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "phone_number",
            "Enter a valid phone number using digits and standard separators.",
        )


class ApplicationShellTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            "shell-member",
            first_name="Sofia",
            last_name="Reyes",
            password=PASSWORD,
        )

    def test_login_uses_official_branding_without_application_navigation(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertContains(response, "/static/assets/branding/CHORD_Logo.png")
        self.assertContains(response, "/static/css/chord.css")
        self.assertContains(response, "/static/js/chord-shell.js")
        self.assertNotContains(response, 'id="application-sidebar"')

    def test_authenticated_shell_shows_only_authorized_navigation(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, 'id="application-sidebar"')
        self.assertContains(response, 'href="/" aria-current="page"')
        self.assertContains(response, reverse("accounts:profile"))
        self.assertNotContains(response, reverse("accounts:user-list"))
        self.assertNotContains(response, reverse("members:list"))

    def test_shell_does_not_advertise_unimplemented_figma_features(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertNotContains(response, ">Bookings<")
        self.assertNotContains(response, ">Recommendations<")
        self.assertNotContains(response, ">Reports<")
        self.assertNotContains(response, ">Notifications<")

    def test_administrator_sees_permission_backed_navigation(self):
        administrator = User.objects.create_user("shell-admin", password=PASSWORD)
        role = Role.objects.get(code=Role.Code.CHURCH_ADMINISTRATOR)
        UserRole.objects.create(user=administrator, role=role)
        self.client.force_login(administrator)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, reverse("accounts:user-list"))
        self.assertContains(response, reverse("members:list"))
        self.assertContains(response, reverse("events:list"))
        self.assertContains(response, reverse("events:attendance-overview"))
        self.assertContains(response, reverse("worship:song-list"))

    def test_shell_marks_current_module_navigation(self):
        administrator = User.objects.create_user("section-admin", password=PASSWORD)
        role = Role.objects.get(code=Role.Code.CHURCH_ADMINISTRATOR)
        UserRole.objects.create(user=administrator, role=role)
        self.client.force_login(administrator)

        response = self.client.get(reverse("members:list"))

        self.assertEqual(response.context["shell_nav_section"], "members")
        self.assertContains(response, ">Members</a>")
        self.assertContains(response, 'aria-current="page"')

    def test_shell_static_assets_are_discoverable(self):
        self.assertIsNotNone(finders.find("assets/branding/CHORD_Logo.png"))
        self.assertIsNotNone(finders.find("assets/branding/CHORD Logo.svg"))
        self.assertIsNotNone(finders.find("css/chord.css"))
        self.assertIsNotNone(finders.find("js/chord-shell.js"))


class AccountManagementTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user("member", password=PASSWORD)
        self.administrator = User.objects.create_user("admin-user", password=PASSWORD)
        admin_role = Role.objects.get(code=Role.Code.CHURCH_ADMINISTRATOR)
        UserRole.objects.create(user=self.administrator, role=admin_role)

    def test_regular_user_cannot_access_account_management(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, 403)

    def test_church_administrator_can_list_accounts(self):
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.username)

    def test_account_list_renders_pagination_controls(self):
        User.objects.bulk_create(
            [User(username=f"page-user-{index}") for index in range(25)]
        )
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, "Next")

    def test_account_role_prefetch_avoids_n_plus_one_queries(self):
        church_member = Role.objects.get(code=Role.Code.CHURCH_MEMBER)
        UserRole.objects.create(user=self.member, role=church_member)

        with self.assertNumQueries(2):
            users = list(UserListView.queryset.all())
            for user in users:
                list(user.roles.all())

    def test_account_create_requires_add_user_permission(self):
        admin_role = Role.objects.get(code=Role.Code.CHURCH_ADMINISTRATOR)
        add_permission = Permission.objects.get(
            content_type__app_label="accounts",
            codename="add_user",
        )
        admin_role.permissions.remove(add_permission)
        self.client.force_login(self.administrator)

        response = self.client.get(reverse("accounts:user-add"))

        self.assertEqual(response.status_code, 403)

    def test_account_creation_assigns_multiple_roles_with_audit_record(self):
        self.client.force_login(self.administrator)
        roles = Role.objects.filter(
            code__in=(Role.Code.CHOIR_MEMBER, Role.Code.CHURCH_MEMBER)
        )
        response = self.client.post(
            reverse("accounts:user-add"),
            {
                "username": "new-member",
                "first_name": "New",
                "last_name": "Member",
                "email": "new@example.test",
                "is_active": "on",
                "roles": [str(role.pk) for role in roles],
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        created_user = User.objects.get(username="new-member")
        self.assertEqual(created_user.roles.count(), 2)
        self.assertFalse(created_user.is_staff)
        self.assertEqual(
            created_user.role_assignments.filter(
                assigned_by=self.administrator
            ).count(),
            2,
        )

    def test_administrator_cannot_deactivate_or_change_own_roles(self):
        self.client.force_login(self.administrator)
        response = self.client.post(
            reverse("accounts:user-edit", args=(self.administrator.pk,)),
            {
                "username": self.administrator.username,
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.test",
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        self.administrator.refresh_from_db()
        self.assertTrue(self.administrator.is_active)
        self.assertTrue(self.administrator.has_role(Role.Code.CHURCH_ADMINISTRATOR))

    def test_administrator_can_deactivate_another_account(self):
        self.client.force_login(self.administrator)
        response = self.client.post(
            reverse("accounts:user-edit", args=(self.member.pk,)),
            {
                "username": self.member.username,
                "first_name": "Church",
                "last_name": "Member",
                "email": "member@example.test",
                "roles": [],
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        self.client.logout()
        self.assertFalse(
            self.client.login(username=self.member.username, password=PASSWORD)
        )

    def test_account_update_reconciles_roles_and_preserves_assignment_audit(self):
        church_member = Role.objects.get(code=Role.Code.CHURCH_MEMBER)
        choir_member = Role.objects.get(code=Role.Code.CHOIR_MEMBER)
        UserRole.objects.create(
            user=self.member,
            role=church_member,
            assigned_by=self.administrator,
        )
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse("accounts:user-edit", args=(self.member.pk,)),
            {
                "username": self.member.username,
                "first_name": "Church",
                "last_name": "Member",
                "email": "member@example.test",
                "is_active": "on",
                "roles": [str(choir_member.pk)],
            },
        )

        self.assertRedirects(response, reverse("accounts:user-list"))
        assignment = self.member.role_assignments.get()
        self.assertEqual(assignment.role, choir_member)
        self.assertEqual(assignment.assigned_by, self.administrator)
