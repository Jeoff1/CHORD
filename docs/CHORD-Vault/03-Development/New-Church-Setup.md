# New Church Setup

How to give a church its own CHORD. Each church gets **its own database**. Never
start a real church from the demo database, and never load demo data into a
real church's database.

| Database | Purpose | Contents |
| --- | --- | --- |
| Demo (e.g. `chord_demo`) | Showing CHORD to churches | `seed_tradition` demo data only |
| One per church (e.g. `chord_gracechurch`) | That church's live system | The church's own data only |

## 1. Create the church's database

In `psql`, as a PostgreSQL administrator (see [[../02-Architecture/Database-Configuration]]):

```sql
CREATE ROLE gracechurch_user WITH LOGIN PASSWORD '<choose-a-strong-password>';
CREATE DATABASE chord_gracechurch OWNER gracechurch_user;
```

Use a new password for each church. Do not reuse the demo password, and never
write passwords in Git, the vault or chat.

## 2. Point a CHORD installation at it

Copy `.env.example` to that installation's `.env` and fill it in:

```ini
DJANGO_SECRET_KEY=<new random key; one per church>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<the church's host name>
DB_NAME=chord_gracechurch
DB_USER=gracechurch_user
DB_PASSWORD=<the password from step 1>
```

Generate a secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For a public deployment, also set the `DJANGO_SECURE_*` and cookie settings.
Production hardening belongs to Phase 9.

## 3. Build the database

```powershell
python manage.py migrate
```

Migrations load everything a church starts with:

- the three Traditions (Roman Catholic, Alliance, Iglesia Ni Cristo), with
  their terminology and default modules;
- common and Tradition roles;
- Themes, Service Templates with Song Slots, and the 2026-27 Church Calendar;
- Church Record Types and songbooks.

They add **no** demo users, members, songs, plans or records. The Church
Profile starts as "My Church" on the Alliance Tradition.

Do **not** run `seed_tradition` here. If someone does by mistake, it refuses once
the profile is renamed or real members exist (see
[[../03-Modules/Church-Profile-Traditions]]). Rename the profile in step 5 straight
away so that this guard is active.

## 4. Create the first administrator

```powershell
python manage.py createsuperuser
```

Give this account to the person who installs CHORD. It can do everything, so
keep it for setup and emergencies, not daily use.

## 5. Set the church profile

Sign in and open **Church Profile** (`/church/`):

1. Enter the church's real name.
2. Choose its Tradition. This changes terminology, roles, themes, templates,
   songbooks, calendar and record types.
3. Turn modules on or off (for example, turn off Giving if the church does not
   want it).

## 6. Create the church's accounts

Open **Users** (`/users/add/`) and create an account for each leader. Assign roles.
Only the common roles and the chosen Tradition's roles are offered. For
example, a Catholic parish would have a Parish Priest (administrator), a Music
Director (worship leader), and Choir Members. Give everyday administration to a
church-administrator role rather than the superuser.

## 7. Enter the church's own data

The church (or you, with them) adds members, ministries, songs in their allowed
songbooks, and worship plans. Check the Church Calendar (`/church/calendar/`)
and adjust movable dates each year.

## 8. Check before handing over

- [ ] The profile shows the real church name and Tradition.
- [ ] No `example.com` accounts or members exist.
- [ ] Each leader can sign in and sees only their permitted areas.
- [ ] Disabled modules are gone from the navigation.
- [ ] Backups of the church's database are scheduled.

## Updating the demo

To refresh the demo, use the demo database only:

```powershell
python manage.py migrate
python manage.py seed_tradition roman-catholic   # or alliance / iglesia-ni-cristo
```

For a clean demo of a single Tradition, drop and recreate the demo database
first. Seeding another Tradition keeps the earlier one's demo data.
