# Database Design

## Phase 2 account schema

- `accounts_user` — custom Django user with a many-to-many role relation.
- `accounts_profile` — one-to-one, small account profile; it intentionally does
  not duplicate future church-member records.
- `accounts_role` — stable code, display name, description, and Django
  permissions.
- `accounts_userrole` — through model with user, role, assigning user, and
  assignment time.
- `accounts_role_permissions` — responsibility permissions granted by a role.

`unique_user_role` prevents duplicate assignments. Deleting a user cascades its
assignments/profile; deleting an assigned role is protected. Deleting an
assigning administrator preserves the assignment but sets `assigned_by` null.

Migration `0002_alter_user_options_profile_role_userrole_user_roles_and_more`
preserves existing users, creates profiles for them, and seeds all six roles.

See [[Architecture-Decisions]] and [[../03-Modules/Authentication]].

## Phase 3 member schema

- `members_member` — UUID-addressed member identity, optional one-to-one user
  link, contact fields, membership status, dates, and timestamps.
- `members_memberauditevent` — application-controlled audit entries storing
  actor, action, timestamp, and changed field names without copied field values.

The user link is optional because not every church record needs login access.
One account can link to at most one member record. Future dates are rejected for
birth and join dates. Search indexes cover name and membership status. Audit
events protect member deletion, and no hard-delete workflow is exposed.

See [[../03-Modules/Member-Management]].

## QA verification

On 2026-11-07, live PostgreSQL introspection confirmed the unique user/role
constraint, one-to-one member/user constraint, unique member UUID, composite
name index, and membership-status index. Migration
`accounts.0003_alter_profile_phone_number` added consistent profile phone
validation without changing stored data.
