from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.tasks import send_telegram_payment_alert
from .models import Donation
from .services import score_suspicious_operation
from .tasks import send_donation_status_email


@receiver(post_save, sender=Donation)
def donation_created(sender, instance: Donation, created: bool, **kwargs):
    if created:
        score_suspicious_operation(instance)
        send_telegram_payment_alert.delay(instance.pk)
        send_donation_status_email.delay(instance.pk)
