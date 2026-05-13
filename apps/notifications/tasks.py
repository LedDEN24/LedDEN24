import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, autoretry_for=(requests.RequestException,), retry_kwargs={"max_retries": 3, "countdown": 20})
def send_telegram_message(self, text: str, chat_id: str | None = None) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    target = chat_id or settings.TELEGRAM_FINANCE_CHAT_ID
    if not token or not target:
        return False
    response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": target, "text": text}, timeout=10)
    response.raise_for_status()
    return True


@shared_task
def send_telegram_payment_alert(donation_id: int) -> bool:
    from apps.donations.models import Donation

    donation = Donation.objects.select_related("project").get(pk=donation_id)
    project = donation.project.title if donation.project else "General fund"
    return send_telegram_message.delay(f"New donation {donation.public_id}: {donation.amount} {donation.currency} via {donation.method} for {project}") is not None


@shared_task
def send_email_notification(subject: str, message: str, recipient: str) -> int:
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
