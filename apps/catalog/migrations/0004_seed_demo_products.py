from django.db import migrations


def seed_demo_products(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    category_map = {
        row.slug: row
        for row in Category.objects.filter(slug__in=["srezka", "bukety", "kompozicii", "cvety-v-korobke"])
    }

    demo_products = [
        {
            "slug": "pionovyj-rassvet",
            "category": "bukety",
            "title": "Пионовый рассвет",
            "price": 4590,
            "image_url": "/static/img/demo-bouquet-blush.svg",
            "description": "Нежный букет в пудровых оттенках для романтичного подарка или важного повода.",
            "is_hit": True,
            "is_new": False,
        },
        {
            "slug": "rozovyj-akcent",
            "category": "bukety",
            "title": "Розовый акцент",
            "price": 3990,
            "image_url": "/static/img/demo-bouquet-rose.svg",
            "description": "Яркий букет с выразительным характером и аккуратной упаковкой в фирменном стиле.",
            "is_hit": False,
            "is_new": True,
        },
        {
            "slug": "korobka-velvet",
            "category": "cvety-v-korobke",
            "title": "Коробка Velvet",
            "price": 6990,
            "image_url": "/static/img/demo-box-premium.svg",
            "description": "Композиция в коробке для эффектного вручения: розы, декоративная зелень и атласная лента.",
            "is_hit": True,
            "is_new": True,
        },
        {
            "slug": "white-mood",
            "category": "kompozicii",
            "title": "White Mood",
            "price": 5890,
            "image_url": "/static/img/demo-composition-white.svg",
            "description": "Светлая воздушная композиция для свадебного настроения, поздравления или нежного интерьера.",
            "is_hit": False,
            "is_new": True,
        },
        {
            "slug": "eucalyptus-touch",
            "category": "kompozicii",
            "title": "Eucalyptus Touch",
            "price": 5490,
            "image_url": "/static/img/demo-composition-white.svg",
            "description": "Композиция с зеленью и мягкими оттенками, которую удобно дарить в офис или домой.",
            "is_hit": False,
            "is_new": False,
        },
        {
            "slug": "monobuket-iz-roz",
            "category": "srezka",
            "title": "Монобукет из роз",
            "price": 2990,
            "image_url": "/static/img/demo-bouquet-rose.svg",
            "description": "Лаконичный монобукет с чистой подачей, когда нужен стильный знак внимания без лишнего декора.",
            "is_hit": True,
            "is_new": False,
        },
    ]

    for row in demo_products:
        category = category_map.get(row["category"])
        if category is None:
            continue
        Product.objects.update_or_create(
            slug=row["slug"],
            defaults={
                "category": category,
                "title": row["title"],
                "price": row["price"],
                "image_url": row["image_url"],
                "description": row["description"],
                "is_active": True,
                "is_hit": row["is_hit"],
                "is_new": row["is_new"],
                "in_stock": True,
                "quantity": 25,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_product_hit_new"),
    ]

    operations = [
        migrations.RunPython(seed_demo_products, migrations.RunPython.noop),
    ]
