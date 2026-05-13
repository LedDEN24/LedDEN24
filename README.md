# LedDEN24

Модульная Django/DRF система проверки объектов недвижимости и контрагентов по открытым источникам.

## Стек

- Python 3.12+
- Django 5+
- PostgreSQL
- Django REST Framework + JWT
- Celery + Redis
- httpx/aiohttp, BeautifulSoup4, Pandas
- Playwright/Selenium-ready dependencies
- Bootstrap UI
- HTML/PDF reports
- pytest

## Структура проекта

```text
accounts/                 # users table and Django admin integration
checks/
  api/                    # serializers, viewsets, DRF routers
  parsers/                # async parser services per source
  repositories/           # persistence layer
  reports/                # HTML/PDF report generation
  services/               # risk score, matching, pipeline orchestration
  tasks/                  # Celery tasks
  models.py               # checks, parser_results, risks, properties, owners, court_cases, debts
config/
  settings.py             # Django/DRF/Celery/cache/PostgreSQL settings
  urls.py                 # admin, JWT, Swagger/OpenAPI, API, web UI
templates/
  checks/                 # dashboard, check form, report, history
tests/                    # pytest coverage
```

## Основной поток

1. Пользователь создает `Check` через UI или `POST /api/checks/`.
2. Celery task `process_check` запускает async `ParserManager`.
3. Каждый parser service выполняет HTTP-запрос с retry, rate limiting, rotation User-Agent, cache и логированием.
4. Результаты сохраняются в `parser_results`, извлеченные сущности - в `properties`, `owners`, `court_cases`, `debts`.
5. `RiskAnalyzer` ищет совпадения и подозрительные признаки, формирует `risks` и итоговый `risk_score`.
6. `ReportGenerator` сохраняет HTML/PDF отчет.

## Источники

Реализованы отдельные parser service-классы:

- ФССП
- ЕФРСБ
- КАД Арбитр
- сайты судов РФ
- Росреестр
- кадастровая карта
- Avito
- Cian
- Domclick
- новости и СМИ
- открытые Telegram-источники
- базы проблемных застройщиков

Классы находятся в `checks/parsers/*.py`. Реальные источники часто требуют CAPTCHA, JS, cookies или официального API, поэтому текущие адаптеры задают расширяемый каркас: URL/params, async transport, extraction через BeautifulSoup и нормализованный payload.

## Запуск

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
celery -A config worker -l info
```

Swagger UI: `/api/docs/`.

JWT:

- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`

Web UI:

- `/` dashboard
- `/checks/new/` страница проверки
- `/checks/history/` история
- `/checks/<id>/report/` отчет
