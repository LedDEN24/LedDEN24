from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.services import create_notification
from apps.notifications.tasks import send_telegram_payment_alert

from .models import Donation
from .tasks import generate_receipt_task


@receiver(post_save, sender=Donation)
def donation_notifications(sender, instance: Donation, created: bool, **kwargs):
    if created:
        if instance.donor_id:
            create_notification(
                recipient=instance.donor,
                title="Donation received",
                body=f"Donation {instance.public_id} is now {instance.get_status_display()}.",
                severity="info",
                metadata={"donation_id": instance.public_id},
            )
        send_telegram_payment_alert.delay(instance.pk)
    elif instance.status == Donation.Status.APPROVED and not instance.receipt_pdf:
        generate_receipt_task.delay(instance.pk)
