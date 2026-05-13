# Global Charity Platform

Production-oriented Django 5 charity / NGO platform with secure donation workflows, REST API, WebSocket notifications, Celery queues, PostgreSQL, Redis, Nginx and Gunicorn.

## Stack

- Django 5, Django REST Framework, SimpleJWT
- PostgreSQL, Redis, Celery
- Django Channels WebSockets
- TailwindCSS UI through Django Templates
- Docker Compose with Nginx + Gunicorn
- Swagger/OpenAPI via drf-spectacular
- Admin audit logs, role-based permissions, 2FA-ready admin stack

## Applications

```text
apps/
  users              # custom user, roles, email verification, saved payment methods
  donations          # donations, transactions, receipts, review workflow
  crypto_payments    # BTC/ETH/USDT wallets and transaction tracking
  cash_requests      # cash meeting requests and collection points
  projects           # charity projects, progress and sitemap
  news               # foundation news
  reports            # CSV exports through Celery
  notifications      # in-app/email/Telegram notifications and WebSockets
  adminpanel         # extended dashboard, permissions and audit middleware
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Site: <http://localhost>
- Django admin: <http://localhost/admin/>
- API docs: <http://localhost/api/v1/docs/>
- OpenAPI schema: <http://localhost/api/v1/schema/>

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

## Local development without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

PostgreSQL and Redis are required. Configure them through `.env`.

## Main API examples

### JWT login

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "donor@example.org",
  "password": "VeryStrongPassword123"
}
```

### Create a card donation

```http
POST /api/v1/donations/
Authorization: Bearer <access>
Content-Type: application/json

{
  "project": 1,
  "amount": "100.00",
  "currency": "USD",
  "method": "visa",
  "purpose": "Emergency medical support",
  "comment": "Thank you",
  "is_anonymous": false,
  "transaction": {
    "provider": "manual_card",
    "provider_reference": "bank-operation-id"
  }
}
```

### Create a crypto donation

```http
POST /api/v1/donations/crypto/
Content-Type: application/json

{
  "project": 1,
  "amount": "250.00",
  "currency": "USD",
  "method": "usdt_trc20",
  "purpose": "Education fund",
  "wallet_id": 1,
  "expected_crypto_amount": "250.00000000"
}
```

### Create a cash meeting request

```http
POST /api/v1/donations/cash/
Content-Type: application/json

{
  "amount": "500.00",
  "currency": "USD",
  "method": "cash",
  "purpose": "General fund",
  "city": "Dubai",
  "preferred_place": "Foundation office",
  "preferred_time": "2026-05-13T15:00:00Z"
}
```

### Approve or reject a donation

```http
POST /api/v1/donations/12/review/
Authorization: Bearer <financial-manager-token>
Content-Type: application/json

{ "status": "approved" }
```

```http
POST /api/v1/donations/12/review/
Authorization: Bearer <financial-manager-token>
Content-Type: application/json

{ "status": "rejected", "reason": "Receipt does not match transfer" }
```

## Security features

- CSRF middleware enabled for template/session flows
- JWT auth for API clients
- Login attempt limiting through django-axes
- DRF throttling and donation-specific throttle scope
- 2FA-ready admin middleware via django-otp
- PostgreSQL ORM queries for SQL injection protection
- Suspicious operation scoring for high-value, anonymous and crypto donations
- Admin action audit logs
- Secure cookie/HSTS/SSL settings for production
- Nginx hardening headers
- reCAPTCHA environment hooks (`RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY`) for integration

## Roles

- `super_admin`: full operational access
- `financial_manager`: donation review, reports, cash requests, crypto payment review
- `moderator`: content and audit visibility
- `donor`: personal cabinet, donation history, receipts and notifications

## WebSocket notifications

Authenticated users can subscribe to:

```text
ws(s)://<host>/ws/notifications/
```

The backend broadcasts new in-app notifications to the `user_<id>` group.

## Deployment notes

1. Set strong `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=false`.
3. Configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Terminate HTTPS at a load balancer or extend the provided Nginx config with certificates.
5. Configure SMTP and Telegram bot credentials.
6. Run `docker compose up --build -d`.
7. Create admin users and assign roles in Django admin.

## Production commands

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py compilemessages
docker compose exec celery celery -A config inspect active
```
