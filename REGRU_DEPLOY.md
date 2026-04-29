# Развёртывание на обычном REG.RU shared hosting (без VPS)

Эта сборка подготовлена под стандартный Linux-хостинг REG.RU с **ispmanager** и поддержкой **Python 3.10**.

## Что на таком тарифе запускать можно
- Django-сайт
- админку
- каталог, корзину, checkout
- SQLite
- медиа и статику
- YooKassa webhook при корректном HTTPS-домене

## Что не нужно запускать на таком тарифе
- Telegram-бот через `python -m bot.runner`
- фоновые long-running процессы
- Playwright-парсер

Бот в этой сборке оставлен в проекте, но на shared hosting REG.RU его лучше **не запускать**.

## Файлы, которые добавлены специально для REG.RU
- `requirements_regru.txt` — облегчённые зависимости под shared hosting
- `.env.regru.example` — готовый пример переменных окружения
- `passenger_wsgi.py` — WSGI-точка входа для Passenger

## Порядок загрузки

### 1. Подготовь хостинг
В панели REG.RU для домена включи:
- CGI
- Python
- Python 3.10

### 2. Подключись по SSH
Перейди в домашний каталог и создай virtualenv на Python 3.10.

Примерно так:
```bash
ls -la /opt/python/*/bin/python
/opt/python/python-3.10.x/bin/python -m venv ~/djangoenv
source ~/djangoenv/bin/activate
python -V
```

### 3. Залей проект в корень сайта
В папку домена, где лежит сайт. Обычно путь похож на:
```bash
/var/www/LOGIN/data/www/your-domain.ru/
```

В этой папке должны лежать:
- `manage.py`
- `apps/`
- `config/`
- `templates/`
- `static/`
- `passenger_wsgi.py`

### 4. Установи зависимости
```bash
cd /var/www/LOGIN/data/www/your-domain.ru
source ~/djangoenv/bin/activate
pip install --upgrade pip
pip install -r requirements_regru.txt
```

### 5. Подготовь `.env`
```bash
cp .env.regru.example .env
```

Потом открой `.env` и укажи:
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `SITE_URL`
- ключи YooKassa, если используешь оплату

Для стандартного shared hosting оставь Telegram-переменные пустыми.

### 6. Поправь `passenger_wsgi.py`
Открой `passenger_wsgi.py` и замени два пути:
- `PROJECT_ROOT`
- `VENV_SITE_PACKAGES`

Пример:
```python
PROJECT_ROOT = '/var/www/LOGIN/data/www/your-domain.ru'
VENV_SITE_PACKAGES = '/var/www/LOGIN/data/djangoenv/lib/python3.10/site-packages'
```

### 7. Прогони миграции
```bash
python manage.py migrate
```

### 8. Собери статику
```bash
python manage.py collectstatic --noinput
```

### 9. Создай администратора
```bash
python manage.py createsuperuser
```

### 10. Перезапусти приложение
В корне сайта:
```bash
touch .restart-app
```

## Что проверить после запуска
- главная страница открывается
- `/admin/` открывается
- изображения из `/media/` грузятся
- оформление заказа работает
- webhook YooKassa доступен по HTTPS

## Важные замечания

### SQLite
Для небольшого проекта на старте это допустимо. Если нагрузка вырастет, переводи проект на MySQL/PostgreSQL.

### Telegram-бот
Этот проект содержит бота на aiogram с polling. На обычном REG.RU shared hosting его не надо запускать. Для бота нужны:
- VPS
- либо переход на webhook-модель внутри Django

### Playwright
В shared hosting сборке не используется и намеренно исключён из `requirements_regru.txt`.
