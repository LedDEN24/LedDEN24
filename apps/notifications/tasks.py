import requests
from celery import shared_task
from django.conf import settings

from apps.donations.models import Donation


@shared_task
def send_telegram_payment_alert(donation_id: int) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_FINANCE_CHAT_ID:
        return
    donation = Donation.objects.get(pk=donation_id)
    text = (
        f"New donation {donation.reference}\n"
        f"Amount: {donation.amount} {donation.currency}\n"
        f"Method: {donation.get_method_display()}\n"
        f"Status: {donation.get_status_display()}"
    )
    requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": settings.TELEGRAM_FINANCE_CHAT_ID, "text": text},
        timeout=10,
    )
