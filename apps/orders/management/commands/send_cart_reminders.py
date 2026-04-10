from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.orders.models import CartSession


class Command(BaseCommand):
    help = "Mark abandoned carts and print reminders for CRM/bot integration"

    def handle(self, *args, **options):
        now = timezone.now()
        first_border = now - timedelta(minutes=30)
        second_border = now - timedelta(hours=24)
        carts = CartSession.objects.filter(status__in=["active", "abandoned"]).prefetch_related("items__product")
        first_sent = 0
        second_sent = 0
        for cart in carts:
            if not cart.items.exists():
                continue
            if cart.last_activity_at <= first_border and not cart.reminder_1_sent_at:
                cart.status = "abandoned"
                cart.reminder_1_sent_at = now
                cart.save(update_fields=["status", "reminder_1_sent_at", "updated_at"])
                first_sent += 1
                self.stdout.write(f"REMINDER1 {cart.session_key}: Корзина сохранена. Вернитесь к заказу.")
            elif cart.last_activity_at <= second_border and cart.reminder_1_sent_at and not cart.reminder_2_sent_at:
                cart.status = "abandoned"
                cart.reminder_2_sent_at = now
                cart.save(update_fields=["status", "reminder_2_sent_at", "updated_at"])
                second_sent += 1
                self.stdout.write(f"REMINDER2 {cart.session_key}: Корзина всё ещё ждёт вас.")
        self.stdout.write(self.style.SUCCESS(f"First reminders: {first_sent}; second reminders: {second_sent}"))
