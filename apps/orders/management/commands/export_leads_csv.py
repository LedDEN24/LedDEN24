import csv
from django.core.management.base import BaseCommand
from apps.orders.models import LeadEvent


class Command(BaseCommand):
    help = "Export lead events to CSV"

    def add_arguments(self, parser):
        parser.add_argument("--path", default="leads_export.csv")

    def handle(self, *args, **options):
        path = options["path"]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "event_type", "product", "order_id", "source", "utm_source", "utm_campaign"])
            for event in LeadEvent.objects.all().order_by("-created_at"):
                writer.writerow([event.id, event.created_at, event.event_type, getattr(event.product, "title", ""), getattr(event.order, "id", ""), event.source, event.utm_source, event.utm_campaign])
        self.stdout.write(self.style.SUCCESS(f"Saved to {path}"))
