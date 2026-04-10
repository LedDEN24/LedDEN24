from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    data = [
        {'name': 'Срезка', 'slug': 'srezka', 'icon': '🌿', 'order': 10},
        {'name': 'Букеты', 'slug': 'bukety', 'icon': '💐', 'order': 20},
        {'name': 'Композиции', 'slug': 'kompozicii', 'icon': '🌸', 'order': 30},
        {'name': 'Цветы в коробке', 'slug': 'cvety-v-korobke', 'icon': '🎁', 'order': 40},
    ]
    for row in data:
        Category.objects.update_or_create(
            slug=row['slug'],
            defaults={
                'name': row['name'],
                'icon': row['icon'],
                'order': row['order'],
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=migrations.RunPython.noop),
    ]
