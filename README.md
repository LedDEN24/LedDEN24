# Global Care Foundation - Django Charity Platform

Production-oriented Django 5 charity / NGO platform with secure donation workflows, REST API, JWT auth, WebSocket notifications, Tailwind UI, PostgreSQL, Redis, Celery, Gunicorn and Nginx.

## What is included

- **Backend:** Django 5, Django REST Framework, SimpleJWT, drf-spectacular OpenAPI.
- **Apps:** `users`, `donations`, `crypto_payments`, `projects`, `news`, `reports`, `notifications`, `adminpanel`, `cash_requests`.
- **Payments:** Visa, Mastercard, Mir, BTC, ETH, USDT ERC20/TRC20, cash handover requests.
- **Donation states:** `pending`, `checking`, `approved`, `rejected` with unique public numbers, uploaded receipts, risk scoring and PDF receipts.
- **Cabinet:** registration, JWT login, email confirmation flow, profile, donation history, notifications and downloadable receipts.
- **Admin operations:** finance dashboard, payment approval/rejection, cash meeting management, CRUD through Django admin/API, CSV reports, audit logs and Telegram alerts.
- **Security:** CSRF, secure headers, rate limiting, password validators, admin 2FA-ready via `django-otp`, audit middleware, HTTPS-ready settings, suspicious donation scoring.
- **Realtime:** Django Channels WebSocket endpoint at `/ws/notifications/?token=<JWT_ACCESS_TOKEN>`.
- **Frontend:** responsive Tailwind templates, dark/light mode, skeleton loading, toast notifications and dashboard charts.
- **SEO:** sitemap, robots.txt, canonical/OpenGraph metadata, RU/EN i18n settings.
- **Deployment:** Dockerfile, docker-compose, Nginx config, Gunicorn, Celery worker/beat, `.env` configuration and GitHub Actions CI.

## Project structure

```text
config/                    Django settings, URLs, ASGI/WSGI, Celery, sitemap
apps/
  users/                   Custom user, registration, JWT profile endpoints, permissions
  donations/               Donation/transaction models, services, admin actions, receipt PDFs
  crypto_payments/         Crypto wallets/payments and confirmation service hooks
  cash_requests/           Cash meeting requests and manager assignment
  projects/                Charity project CRUD and public detail pages
  news/                    Foundation news CRUD and public detail pages
  notifications/           In-app notifications, WebSocket consumer, email/Telegram tasks
  reports/                 CSV report generation and report API
  adminpanel/              Finance dashboard, stats API and admin audit logs
templates/                 Tailwind Django templates
static/                    CSS/JS assets
nginx/                     Reverse proxy config
.github/workflows/ci.yml   CI checks
```

## Local development

```bash
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Without `DATABASE_URL`, settings fall back to SQLite for quick local checks. Docker uses PostgreSQL by default.

## Docker deployment

```bash
cp .env.example .env
# edit secrets, hosts, email, Telegram and secure cookie settings
docker compose up --build
```

Services:

- `web`: Gunicorn + Django
- `postgres`: PostgreSQL 16
- `redis`: Redis 7 broker/cache layer
- `celery`: async receipt/notification/report tasks
- `celery-beat`: scheduled crypto polling hook
- `nginx`: static/media serving, reverse proxy and WebSocket upgrade

## API examples

OpenAPI docs are available at:

- Swagger: `/api/docs/`
- ReDoc: `/api/redoc/`
- Schema: `/api/schema/`

### Register and obtain JWT

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"donor1","email":"donor@example.org","password":"VeryStrongPass123!"}'

curl -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"donor1","password":"VeryStrongPass123!"}'
```

### Create a card donation

```bash
curl -X POST http://localhost:8000/api/donations/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <access>' \
  -d '{"amount":"100.00","currency":"USD","method":"visa","purpose":"Medical support","comment":"Thank you","is_anonymous":false}'
```

### Approve a donation as financial manager

```bash
curl -X POST http://localhost:8000/api/donations/1/approve/ \
  -H 'Authorization: Bearer <finance-access>'
```

### Download receipt

```bash
curl -L http://localhost:8000/api/donations/1/receipt/ \
  -H 'Authorization: Bearer <access>' \
  -o receipt.pdf
```

### WebSocket notifications

```text
ws://localhost:8000/ws/notifications/?token=<JWT_ACCESS_TOKEN>
```

## Core data model

- `users.User`: custom user with donor/moderator/finance/super-admin roles.
- `projects.Project`: fundraising goals, raised amount, SEO and status.
- `donations.Donation`: public ID, amount, method, status, receipt uploads, anonymous flag, risk score.
- `donations.Transaction`: manual bank, crypto or cash transaction record.
- `crypto_payments.CryptoWallet` / `CryptoPayment`: wallet registry and crypto transfer tracking.
- `cash_requests.CashMeeting`: city, preferred meeting time, assigned manager and status.
- `notifications.Notification`: in-app/email/Telegram-ready notification records.
- `reports.Report`: generated exports.
- `adminpanel.AdminLog`: admin action audit trail.

## Security notes

Before production release:

1. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, production `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.
2. Enable HTTPS at the load balancer and set `SECURE_SSL_REDIRECT=true`, `SESSION_COOKIE_SECURE=true`, `CSRF_COOKIE_SECURE=true`.
3. Configure SMTP and Telegram bot credentials.
4. Enroll admin users in TOTP devices via `django-otp`.
5. Replace placeholder crypto polling in `apps/crypto_payments/tasks.py` with signed integrations to trusted blockchain explorers or payment processors.
6. Configure object storage for uploaded receipts/reports in high-traffic deployments.
7. Review legal/AML/KYC requirements for supported jurisdictions.

## Useful endpoints

- `/` - NGO landing page
- `/donate/` - responsive donation form
- `/dashboard/` - donor cabinet
- `/platform/dashboard/` - finance/admin dashboard
- `/admin/` - Django admin with CRUD and approval actions
- `/api/donations/` - donation API
- `/api/projects/` - project API
- `/api/news/` - news API
- `/api/reports/donations-export/` - report export
