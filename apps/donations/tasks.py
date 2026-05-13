from celery import shared_task

from .models import Donation
from .services import generate_receipt_pdf


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 30})
def generate_receipt_task(self, donation_id: int) -> str:
    donation = Donation.objects.get(pk=donation_id)
    generate_receipt_pdf(donation)
    return donation.public_id
