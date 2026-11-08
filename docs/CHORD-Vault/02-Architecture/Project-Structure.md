# Project Structure

- `config/` — Django settings, root URLs, ASGI, and WSGI
- `apps/accounts/` — foundational custom user app
- `templates/`, `static/`, `media/` — shared project assets
- `docs/CHORD-Vault/` — Obsidian-compatible source-of-truth notes
- `.venv/` — active project-specific Python environment (untracked)
- `.env` — local secrets and environment configuration (untracked)
- `requirements.txt` — exact reproducible Python package versions
- `manage.py` — Django command entry point
- `apps/members/` — member records, privacy-aware directory, audit events, and tests
- `apps/validators.py` — shared model-level input validators
- `templates/includes/` — reusable presentation fragments such as pagination

`AUTH_USER_MODEL` is `accounts.User`. `Role` and the auditable `UserRole`
through model support multiple roles per user. Choir participation is not a role
assignment and belongs in the future choir domain.

See [[../01-Project/Project-Overview]] and [[Database-Configuration]].
