# Project Structure

- `config/` - Django settings, root URLs, ASGI, and WSGI
- `apps/accounts/` - custom user, profiles, roles, and permission backend
- `apps/members/` - member records, privacy-aware directory, and audit events
- `apps/worship/` - choir enrollment, rehearsals, songs, resources, and plans
- `apps/validators.py` - shared model-level input and upload validators
- `templates/` - shared Bootstrap presentation and app templates
- `templates/includes/` - reusable fragments such as filter-safe pagination
- `static/`, `media/` - public/static project assets
- `protected_media/` - untracked licensed worship files, never publicly served
- `docs/CHORD-Vault/` - Obsidian-compatible source-of-truth notes
- `.venv/` - active project-specific Python environment (untracked)
- `.env` - local secrets and environment configuration (untracked)
- `requirements.txt` - exact reproducible Python package versions
- `manage.py` - Django command entry point

`AUTH_USER_MODEL` is `accounts.User`. `Role` and the auditable `UserRole`
through model support multiple roles per user. `ChoirEnrollment` links the
existing member record to domain participation without duplicating a role or
member identity. Licensed files are streamed through a permission-checked view.

See [[../01-Project/Project-Overview]] and [[Database-Configuration]].
