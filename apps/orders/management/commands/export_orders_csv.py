import csv
from django.core.management.base import BaseCommand
from apps.orders.models import Order


class Command(BaseCommand):
    help = "Export orders to CSV"

    def add_arguments(self, parser):
        parser.add_argument("--path", default="orders_export.csv")

    def handle(self, *args, **options):
        path = options["path"]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "status", "stage", "name", "phone", "total", "source", "utm_source", "utm_campaign"])
            for order in Order.objects.all().order_by("-created_at"):
                writer.writerow([order.id, order.created_at, order.status, order.stage, order.name, order.phone, order.total, order.source, order.utm_source, order.utm_campaign])
        self.stdout.write(self.style.SUCCESS(f"Saved to {path}"))
