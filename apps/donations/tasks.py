from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.notifications.services import create_notification
from .models import Donation, Transaction


@shared_task
def send_donation_status_email(donation_id: int) -> None:
    donation = Donation.objects.get(pk=donation_id)
    if not donation.donor_email:
        return
    send_mail(
        subject=f"Donation {donation.reference}: {donation.get_status_display()}",
        message=f"Thank you for supporting our foundation. Current status: {donation.get_status_display()}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[donation.donor_email],
        fail_silently=True,
    )


@shared_task
def generate_receipt_pdf(donation_id: int) -> None:
    donation = Donation.objects.select_related("project").get(pk=donation_id)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Receipt {donation.reference}")
    pdf.drawString(72, 800, "Global Charity Platform")
    pdf.drawString(72, 760, f"Receipt: {donation.reference}")
    pdf.drawString(72, 735, f"Amount: {donation.amount} {donation.currency}")
    pdf.drawString(72, 710, f"Purpose: {donation.purpose}")
    pdf.drawString(72, 685, f"Project: {donation.project.title if donation.project else 'General fund'}")
    pdf.drawString(72, 660, f"Status: {donation.get_status_display()}")
    pdf.showPage()
    pdf.save()
    transaction, _ = Transaction.objects.get_or_create(donation=donation, defaults={"provider": Transaction.Provider.MANUAL_CARD})
    transaction.receipt.save(f"{donation.reference}.pdf", ContentFile(buffer.getvalue()), save=True)


@shared_task
def notify_donor_in_app(donation_id: int) -> None:
    donation = Donation.objects.select_related("donor").get(pk=donation_id)
    if donation.donor_id:
        create_notification(
            recipient=donation.donor,
            title=f"Donation {donation.reference}",
            message=f"Your donation status is {donation.get_status_display()}.",
            level="success" if donation.status == Donation.Status.APPROVED else "info",
        )
