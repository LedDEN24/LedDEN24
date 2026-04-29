from datetime import date, timedelta

from django.db import migrations


def seed_demo_content(apps, schema_editor):
    SiteProfile = apps.get_model("content", "SiteProfile")
    Review = apps.get_model("content", "Review")

    profile = SiteProfile.objects.first()
    if profile is None:
        SiteProfile.objects.create(
            name="Atrium Flowers",
            subtitle="Свежие букеты и композиции с доставкой по городу день в день",
            description=(
                "Собираем нежные букеты, композиции в коробках и подарочные наборы. "
                "Помогаем выбрать букет под повод, настроение и бюджет."
            ),
            phone="+7 (999) 123-45-67",
            address="Екатеринбург, Краснолесья 10/3",
            tg_url="",
            vk_url="",
            maps_url="https://yandex.ru/maps/",
            work_hours="Ежедневно 09:00-22:00",
            yandex_rating=4.9,
            yandex_reviews_count=128,
        )

    if not Review.objects.exists():
        today = date.today()
        Review.objects.bulk_create(
            [
                Review(
                    author="Мария",
                    stars=5,
                    text="Очень аккуратный букет, доставили вовремя и красиво оформили открытку.",
                    created_at=today - timedelta(days=4),
                ),
                Review(
                    author="Игорь",
                    stars=5,
                    text="Заказал композицию в коробке, флорист помог подобрать цвета и все выглядело дорого.",
                    created_at=today - timedelta(days=7),
                ),
                Review(
                    author="Анна",
                    stars=5,
                    text="Нравится, что можно быстро обсудить заказ и получить фото перед отправкой.",
                    created_at=today - timedelta(days=11),
                ),
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0002_alter_siteprofile_maps_url_alter_siteprofile_name_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_demo_content, migrations.RunPython.noop),
    ]
