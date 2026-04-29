# Deploy

## Local / VPS
1. `python -m venv venv`
2. `pip install -r requirements.txt`
3. `cp .env.example .env`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py collectstatic --noinput`
7. `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

## Bot
`python -m bot.runner`

## Reminders
Запускай по cron:
`python manage.py send_cart_reminders`
