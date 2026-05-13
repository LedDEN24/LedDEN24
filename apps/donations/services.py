from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.notifications.services import create_notification

from .models import Donation, Transaction

HIGH_VALUE_THRESHOLD = Decimal("10000.00")


def score_donation_risk(donation: Donation) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []
    if donation.amount >= HIGH_VALUE_THRESHOLD:
        score += 50
        reasons.append("high_value")
    if donation.is_anonymous and donation.amount >= Decimal("1000.00"):
        score += 25
        reasons.append("anonymous_high_value")
    if donation.method in {Donation.Method.BTC, Donation.Method.ETH, Donation.Method.USDT_TRC20, Donation.Method.USDT_ERC20}:
        score += 10
        reasons.append("crypto")
    return min(score, 100), ",".join(reasons)


@transaction.atomic
def register_donation(*, donor=None, ip_address=None, user_agent="", **data) -> Donation:
    donation = Donation(donor=donor, ip_address=ip_address, user_agent=user_agent[:512], **data)
    donation.risk_score, donation.suspicious_reason = score_donation_risk(donation)
    if donation.risk_score >= 50:
        donation.status = Donation.Status.CHECKING
    donation.save()
    gateway = Transaction.Gateway.CASH if donation.method == Donation.Method.CASH else Transaction.Gateway.CRYPTO if donation.method in {Donation.Method.BTC, Donation.Method.ETH, Donation.Method.USDT_TRC20, Donation.Method.USDT_ERC20} else Transaction.Gateway.MANUAL_BANK
    Transaction.objects.create(donation=donation, gateway=gateway, amount=donation.amount, currency=donation.currency, status=donation.status)
    return donation


@transaction.atomic
def approve_donation(donation: Donation, manager) -> Donation:
    if donation.status == Donation.Status.APPROVED:
        return donation
    donation.status = Donation.Status.APPROVED
    donation.approved_by = manager
    donation.approved_at = timezone.now()
    donation.rejected_reason = ""
    donation.save(update_fields=["status", "approved_by", "approved_at", "rejected_reason", "updated_at"])
    donation.transactions.update(status=Donation.Status.APPROVED, checked_by=manager, checked_at=timezone.now())
    if donation.project_id:
        project = donation.project
        project.raised_amount = project.raised_amount + donation.amount
        if project.raised_amount >= project.goal_amount:
            project.status = project.Status.FUNDED
        project.save(update_fields=["raised_amount", "status", "updated_at"])
    if donation.donor_id:
        create_notification(
            recipient=donation.donor,
            title="Donation approved",
            body=f"Your donation {donation.public_id} has been approved.",
            severity="success",
            metadata={"donation_id": donation.public_id},
        )
    return donation


@transaction.atomic
def reject_donation(donation: Donation, manager, reason: str = "") -> Donation:
    donation.status = Donation.Status.REJECTED
    donation.rejected_reason = reason[:255]
    donation.approved_by = None
    donation.approved_at = None
    donation.save(update_fields=["status", "rejected_reason", "approved_by", "approved_at", "updated_at"])
    donation.transactions.update(status=Donation.Status.REJECTED, checked_by=manager, checked_at=timezone.now())
    if donation.donor_id:
        create_notification(
            recipient=donation.donor,
            title="Donation rejected",
            body=reason or f"Donation {donation.public_id} was rejected after verification.",
            severity="warning",
            metadata={"donation_id": donation.public_id},
        )
    return donation


def generate_receipt_pdf(donation: Donation) -> Donation:
    buffer = BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    page.setTitle(f"Receipt {donation.public_id}")
    page.setFont("Helvetica-Bold", 18)
    page.drawString(72, 780, "Global Care Foundation - Donation Receipt")
    page.setFont("Helvetica", 11)
    lines = [
        f"Receipt number: {donation.public_id}",
        f"Date: {(donation.approved_at or donation.created_at):%Y-%m-%d %H:%M UTC}",
        f"Donor: {'Anonymous' if donation.is_anonymous else (donation.donor_name or donation.donor_email or donation.donor or 'Guest')}",
        f"Amount: {donation.amount} {donation.currency}",
        f"Payment method: {donation.get_method_display()}",
        f"Purpose: {donation.purpose or 'General charity programs'}",
        f"Project: {donation.project.title if donation.project else 'General fund'}",
        f"Status: {donation.get_status_display()}",
        f"Authorized by: {settings.DONATION_RECEIPT_SIGNATORY}",
    ]
    y = 740
    for line in lines:
        page.drawString(72, y, str(line))
        y -= 24
    page.showPage()
    page.save()
    buffer.seek(0)
    donation.receipt_pdf.save(f"{donation.public_id}.pdf", ContentFile(buffer.read()), save=True)
    return donation
