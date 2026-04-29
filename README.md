# Atrium Flowers

Готовый Django + Telegram bot проект для цветочного магазина с обновлённой витриной,
корзиной, оформлением заказа и демо-наполнением для быстрого старта.

## Что внутри
- современная главная страница цветочного магазина
- каталог товаров, карточки товара и быстрый поиск
- корзина и оформление заказа
- Telegram bot на aiogram 3
- CRM-поля в заказе и статусы workflow
- аналитика лидов и источников
- брошенная корзина и CSV-выгрузки
- демо-товары, отзывы и способы доставки через миграции

## Быстрый старт
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После `migrate` проект сам создаст:
- профиль магазина
- стартовые отзывы
- демо-товары и категории
- варианты доставки и тайм-слоты

## Бот
```bash
python -m bot.runner
```

## Полезные команды
```bash
python manage.py export_orders_csv --path orders.csv
python manage.py export_leads_csv --path leads.csv
python manage.py send_cart_reminders
```

## Что уже исправлено
- обновлён дизайн витрины, контактов и checkout
- исправлен шаблон страницы товара
- убраны шаблонные и пустые состояния на главной
- добавлено стартовое наполнение для пустой базы


## REG.RU shared hosting
Для обычного REG.RU без VPS используй отдельную инструкцию `REGRU_DEPLOY.md` и зависимости `requirements_regru.txt`.
Telegram-бот на таком тарифе в текущем виде не запускается: размещай только сайт Django.
