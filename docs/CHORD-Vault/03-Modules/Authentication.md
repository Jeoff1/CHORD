# Authentication and RBAC

Status: **Completed — Phase 2 (2026-11-06)**

## Implemented

- Django session login and CSRF-protected POST logout
- Password change while retaining the authenticated session
- Automatic one-to-one profile and self-only profile editing
- Six seeded roles with multiple-role support
- Audited and unique role assignments
- Role-to-Django-permission backend
- Scoped account listing, creation, editing, activation/deactivation, and role
  assignment for authorized Church Administrators
- Protection against self-deactivation and self-role changes
- Django admin integration for users, profiles, roles, and assignments
- Bootstrap 5 template foundation and authenticated navigation

## Permission boundary

The Church Administrator role receives the exact account and member permissions
defined in code. It does not imply access to giving or other future confidential
modules. Other roles receive permissions only when an implemented workflow
requires them. All enforcement is server-side; template visibility is only a
usability aid. Permission synchronization removes stale administrator grants.

## Bootstrap procedure

Use `python manage.py createsuperuser` for the first trusted local operator,
then add a Church Administrator assignment in `/admin/`. Superuser status and
the ordinary application role remain conceptually separate.

Bootstrap status: completed and verified on 2026-11-06. One active Church
Administrator assignment exists. Account identifiers and credentials are not
recorded in documentation.

## Not included

Password-reset email, member records, ministry/choir participation, and future
domain permissions are outside Phase 2.

See [[../01-Project/User-Roles]], [[../02-Architecture/Database-Design]], and
[[../04-Testing/Phase-2-Test-Results]].
