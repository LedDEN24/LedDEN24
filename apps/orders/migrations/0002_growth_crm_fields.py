from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_product_hit_new"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CartSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(max_length=64, unique=True)),
                ("tg_user_id", models.CharField(blank=True, default="", max_length=50)),
                ("username", models.CharField(blank=True, default="", max_length=100)),
                ("phone", models.CharField(blank=True, default="", max_length=50)),
                ("status", models.CharField(choices=[("active", "active"), ("abandoned", "abandoned"), ("recovered", "recovered"), ("converted", "converted")], default="active", max_length=20)),
                ("source", models.CharField(blank=True, default="site", max_length=50)),
                ("utm_source", models.CharField(blank=True, default="", max_length=120)),
                ("utm_medium", models.CharField(blank=True, default="", max_length=120)),
                ("utm_campaign", models.CharField(blank=True, default="", max_length=120)),
                ("last_activity_at", models.DateTimeField(auto_now=True)),
                ("reminder_1_sent_at", models.DateTimeField(blank=True, null=True)),
                ("reminder_2_sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.AddField(model_name="order", name="stage", field=models.CharField(choices=[("new", "Новый"), ("in_progress", "В работе"), ("waiting_client", "Ждёт клиента"), ("agreed", "Согласован"), ("paid", "Оплачен"), ("completed", "Выполнен"), ("cancelled", "Отменён")], default="new", max_length=20)),
        migrations.AddField(model_name="order", name="manager_name", field=models.CharField(blank=True, default="", max_length=120)),
        migrations.AddField(model_name="order", name="manager_comment", field=models.TextField(blank=True, default="")),
        migrations.AddField(model_name="order", name="next_contact_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="order", name="priority", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="order", name="customer_tag", field=models.CharField(blank=True, default="", max_length=80)),
        migrations.AddField(model_name="order", name="source", field=models.CharField(blank=True, default="site", max_length=50)),
        migrations.AddField(model_name="order", name="session_key", field=models.CharField(blank=True, default="", max_length=64)),
        migrations.AddField(model_name="order", name="utm_source", field=models.CharField(blank=True, default="", max_length=120)),
        migrations.AddField(model_name="order", name="utm_medium", field=models.CharField(blank=True, default="", max_length=120)),
        migrations.AddField(model_name="order", name="utm_campaign", field=models.CharField(blank=True, default="", max_length=120)),
        migrations.CreateModel(
            name="LeadEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("telegram_id", models.CharField(blank=True, default="", max_length=50)),
                ("session_key", models.CharField(blank=True, default="", max_length=64)),
                ("event_type", models.CharField(choices=[("product_view", "product_view"), ("add_to_cart", "add_to_cart"), ("cart_remove", "cart_remove"), ("checkout_start", "checkout_start"), ("checkout_submit", "checkout_submit"), ("payment_success", "payment_success"), ("payment_fail", "payment_fail"), ("manager_contact", "manager_contact")], max_length=40)),
                ("source", models.CharField(blank=True, default="", max_length=50)),
                ("utm_source", models.CharField(blank=True, default="", max_length=120)),
                ("utm_medium", models.CharField(blank=True, default="", max_length=120)),
                ("utm_campaign", models.CharField(blank=True, default="", max_length=120)),
                ("metadata_json", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="orders.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="catalog.product")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price_snapshot", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cart_session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.cartsession")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="catalog.product")),
            ],
            options={"unique_together": {("cart_session", "product")}},
        ),
        migrations.AddField(model_name="cartsession", name="converted_order", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="converted_carts", to="orders.order")),
    ]
