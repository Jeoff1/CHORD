# Database Configuration

PostgreSQL 17.11 is running as `postgresql-x64-17` and accepts connections on
local port 5432. The `chord_db` database and `chord_user` login exist. Django
connects successfully as that dedicated user, and all initial migrations have
been applied.

## Local test privilege

The application role has `CREATEDB` so Django can create its isolated test
database. This was enabled in pgAdmin with:

```sql
ALTER ROLE chord_user CREATEDB;
```

This local-development privilege allows Django to create and remove
`test_chord_db`. It does not grant superuser or role-management access. The full
test suite passed, Django destroyed the test database, and a follow-up query
confirmed that `test_chord_db` does not remain.

## Original creation procedure

1. Open pgAdmin 4 and connect to the local PostgreSQL 17 server using the
   administrator password. Do not share or document that password.
2. Open **Tools > Query Tool** for the `postgres` database.
3. Choose a strong, project-specific password locally and run the following,
   replacing the placeholder only inside pgAdmin:

```sql
CREATE ROLE chord_user WITH LOGIN PASSWORD '<choose-a-local-password>'
    NOSUPERUSER CREATEDB NOCREATEROLE NOINHERIT;
CREATE DATABASE chord_db OWNER chord_user;
```

`CREATEDB` is included for this local development role so Django's test runner
can create and remove isolated test databases. It does not grant superuser,
role-management, or access to unrelated database objects.

Before running the statements, check **Login/Group Roles** and **Databases**. If
either object already exists, do not recreate, delete, or reset it. Instead,
confirm that `chord_user` owns `chord_db`; ask for review if it does not.

4. Put the same application password in the untracked `.env` value
   `DB_PASSWORD`. Never put it in source, Git, terminal history, or this vault.
5. Activate `.venv`, run `python manage.py migrate`, then `python manage.py test`.

The app uses `django.db.backends.postgresql`, database `chord_db`, application
role `chord_user`, host `localhost`, and port `5432`. It does not use the
PostgreSQL superuser at runtime and no public-network configuration was changed.
The password is present only in the ignored `.env` and is not documented.

See [[Environment-Setup]] and [[../03-Development/Known-Issues]].
