# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

This is a Django-based flower shop ("Atrium Flowers") with a Telegram bot integration. The `main` branch is empty; active development happens on feature branches (most complete: `cursor/atrium-store-redesign-97e1`).

### Services

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| Django web | `python manage.py runserver 0.0.0.0:8000` | 8000 | Main storefront + admin |
| Telegram bot | `python -m bot.runner` | — | Requires `TG_BOT_TOKEN` in `.env` |

### Quick Start (after update script has run)

```bash
source /workspace/venv/bin/activate
cp .env.example .env  # if .env doesn't exist
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Key Development Notes

- **Settings module**: `config.settings.local` (set by `manage.py`). SQLite is the default DB; PostgreSQL is optional via `DATABASE_URL` in `.env`.
- **Demo data**: Migrations auto-seed demo products, categories, reviews, delivery options, and a site profile. No manual fixtures needed.
- **Superuser**: Create via `DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin123 DJANGO_SUPERUSER_EMAIL=admin@example.com python manage.py createsuperuser --noinput`
- **Tests**: `python manage.py test apps.orders.tests -v 2` (9 tests covering e-commerce flow, cart, payments, notifications).
- **Lint**: `flake8 apps/ config/ --max-line-length=120` (existing style issues are pre-existing, not regressions).
- **Static files**: Served from `/workspace/static/` in dev mode (no `collectstatic` needed for development).
- **Telegram bot**: Won't start without a valid `TG_BOT_TOKEN`; this is expected and does not block web development.
- **Payment integration**: YooKassa gateway requires `YOOKASSA_SHOP_ID` and `YOOKASSA_SECRET_KEY` in `.env`; mocked in tests.
