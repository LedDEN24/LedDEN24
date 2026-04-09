# LedDEN24

Готовый стартовый сайт на Django с адаптивной главной страницей, секциями услуг,
преимуществ и контактов.

## Что внутри

- Django 6
- приложение `main`
- шаблоны и стили для главной страницы
- базовые тесты для проверки доступности сайта

## Запуск проекта

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

После запуска сайт будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Запуск тестов

```bash
python3 manage.py test
```
