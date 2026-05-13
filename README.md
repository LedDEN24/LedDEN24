# Real Estate Due Diligence Platform

Backend for automated Russian real-estate due diligence. The project provides a
modular parser architecture, async task orchestration, risk scoring, AI-assisted
summaries, report generation, RBAC-ready APIs, audit logging, and Docker-based
local infrastructure.

## Stack

- Python 3.12+, Django 5, Django REST Framework
- PostgreSQL, Redis, Celery
- httpx/aiohttp-ready async parser layer, BeautifulSoup/lxml, Playwright/Selenium hooks
- JWT authentication, RBAC permissions, encrypted personal data fields
- Elasticsearch integration point for search indexing
- Pandas exports, HTML/PDF/JSON/XLSX reports
- Optional OpenAI-compatible LLM risk analysis
- Docker Compose, Prometheus/Grafana, Flower

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API entry points:

- `POST /api/v1/checks/` - create a property check
- `POST /api/v1/checks/{id}/run/` - enqueue parsing and analysis
- `GET /api/v1/checks/{id}/report/?format=json|html|pdf|xlsx` - download report
- `GET /api/v1/checks/{id}/risks/` - risk findings

Detailed API examples are in [docs/API.md](docs/API.md).

## Architecture

The parser layer is source-oriented: every public source is represented by a
dedicated parser service class registered in `parsers.sources`. A parser uses the
shared base class and infrastructure services for:

- async execution
- proxy and user-agent rotation
- rate limiting and retry policy
- cache lookups
- anti-ban/captcha abstraction
- structured logging and result normalization

Celery task `apps.checks.tasks.run_property_check` coordinates parser execution,
aggregation, deterministic risk scoring, optional LLM analysis, persistence, and
report generation readiness.

## Local checks

```bash
python3 -m compileall .
python3 -m unittest discover -s tests
```

## Security notes

Personal data fields use an encrypted Django field abstraction. Configure a
stable `FIELD_ENCRYPTION_KEY` in production and keep all secrets outside source
control. Audit log records are written for API actions and parser lifecycle
events. DRF throttling is enabled in settings and should be tuned per deployment.
