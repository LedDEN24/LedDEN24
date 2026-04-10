from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_seed_default_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_hit",
            field=models.BooleanField("Хит", default=False, db_index=True),
        ),
        migrations.AddField(
            model_name="product",
            name="is_new",
            field=models.BooleanField("Новый", default=False, db_index=True),
        ),
    ]
