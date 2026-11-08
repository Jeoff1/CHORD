# CHORD

CHORD is a Django-based church management system. Completed phases provide
secure authentication, responsibility-based access control, and privacy-aware
member management. Future phases will add ministries, attendance, giving,
worship planning, reporting, and ML-assisted song recommendations.

## Technology stack

- Python 3.14.7
- Django 5.2.19 LTS
- PostgreSQL 17.11 with psycopg 3.3.8
- python-dotenv 1.2.4
- Ruff 0.17.4

## Local setup

Create and activate the project environment in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

In VS Code, run **Python: Select Interpreter** and select
`.venv\Scripts\python.exe`.

## Database configuration

PostgreSQL must contain a locally accessible database named `chord_db` owned by
the non-superuser role `chord_user`. Copy `.env.example` to `.env`, generate a
development secret key, and set the database password only in `.env`.
Never commit `.env`.

See [[docs/CHORD-Vault/02-Architecture/Database-Configuration]] for the pgAdmin
setup procedure.

## Development commands

After activating `.venv` and configuring the database:

```powershell
python manage.py migrate
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py test
python -m ruff check .
python manage.py runserver
```

The development site will be available at <http://127.0.0.1:8000/>.

## Authentication bootstrap

The six CHORD roles are seeded by migrations. To create the first trusted local
operator, run `python manage.py createsuperuser`, sign in at `/admin/`, and add a
Church Administrator role assignment. Django superuser status is an emergency
framework-level capability; the ordinary Church Administrator role only grants
the scoped account-management permissions documented for Phase 2.

Application users sign in at `/login/`. Authenticated users can update their own
small account profile and password. Church Administrators can create, activate,
deactivate, and assign multiple roles to accounts without receiving permissions
for future confidential modules.

Member management is available at `/members/` to authorized users. Linked
accounts can open `/members/me/` to view only their own member record.

## Production security switches

The `.env.example` file documents secure-cookie, HTTPS redirect, and HSTS
settings. Their local defaults remain disabled so HTTP development works. Set
them only behind a correctly configured production HTTPS endpoint, then run
`python manage.py check --deploy` with production environment values.
