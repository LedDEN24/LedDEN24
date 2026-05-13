# LedDEN24

Django 5 / DRF система проверки недвижимости и участников сделки по открытым источникам.

## Структура

```text
config/                    # settings.py, urls.py, Celery, ASGI/WSGI
accounts/                  # кастомная users-модель
checks/
  models.py                # checks, parser_results, risks, properties, owners, court_cases, debts
  admin.py                 # Django admin
  api/                     # serializers, views, urls
  repositories/            # сохранение результатов и агрегатов
  services/
    parsers/               # base class, registry, async manager, parser services
    risk_analyzer.py       # risk score и подозрительные признаки
  tasks/                   # Celery tasks
  reports/                 # HTML/PDF генерация
  templates/checks/        # dashboard, проверка, отчет, история
tests/                     # pytest
```

## Источники парсеров

Реализованы отдельные parser service классы для ФССП, ЕФРСБ, КАД Арбитр,
сайтов судов РФ, Росреестра, кадастровой карты, Avito, Cian, Domclick,
новостей/СМИ, открытых Telegram-источников и баз проблемных застройщиков.

Базовый parser service содержит:

- async parsing через `httpx.AsyncClient`;
- retry logic;
- обработку ошибок и логирование;
- rate limiting;
- rotation user-agent;
- кэширование через Django cache;
- поиск совпадений по адресу, кадастровому номеру, ФИО, телефону, email и ИНН.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
celery -A config worker -l info
python manage.py runserver
```

Swagger/OpenAPI: `/api/docs/`.
JWT: `/api/auth/token/`, `/api/auth/token/refresh/`.

## Тесты

```bash
pytest
```
