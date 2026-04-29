from datetime import time, timedelta

from django.db import migrations
from django.utils import timezone


def seed_delivery_data(apps, schema_editor):
    DeliveryOption = apps.get_model("orders", "DeliveryOption")
    DeliverySlot = apps.get_model("orders", "DeliverySlot")

    courier, _ = DeliveryOption.objects.get_or_create(
        name="Курьером",
        defaults={"price": 350, "is_active": True, "sort": 1},
    )
    pickup, _ = DeliveryOption.objects.get_or_create(
        name="Самовывоз",
        defaults={"price": 0, "is_active": True, "sort": 2},
    )

    if not DeliverySlot.objects.exists():
        base_date = timezone.localdate() + timedelta(days=1)
        slots = [
            (courier, base_date, time(10, 0), time(13, 0)),
            (courier, base_date, time(14, 0), time(17, 0)),
            (courier, base_date, time(18, 0), time(21, 0)),
            (pickup, base_date, time(12, 0), time(20, 0)),
        ]
        for option, slot_date, time_from, time_to in slots:
            DeliverySlot.objects.create(
                delivery_option=option,
                date=slot_date,
                time_from=time_from,
                time_to=time_to,
                capacity=10,
                reserved_count=0,
                is_active=True,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0004_order_workflow_status_deliveryslot_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_delivery_data, migrations.RunPython.noop),
    ]
