from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def receipt_upload_path(instance, filename: str) -> str:
    return f"receipts/{instance.public_id}/{filename}"


class Donation(models.Model):
    class Method(models.TextChoices):
        VISA = "visa", "Visa"
        MASTERCARD = "mastercard", "Mastercard"
        MIR = "mir", "Mir"
        BTC = "btc", "Bitcoin"
        ETH = "eth", "Ethereum"
        USDT_TRC20 = "usdt_trc20", "USDT TRC20"
        USDT_ERC20 = "usdt_erc20", "USDT ERC20"
        CASH = "cash", _("Cash")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CHECKING = "checking", _("Checking")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    class Currency(models.TextChoices):
        USD = "USD", "USD"
        EUR = "EUR", "EUR"
        RUB = "RUB", "RUB"
        BTC = "BTC", "BTC"
        ETH = "ETH", "ETH"
        USDT = "USDT", "USDT"

    public_id = models.CharField(max_length=32, unique=True, editable=False)
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
    donor_name = models.CharField(max_length=180, blank=True)
    donor_email = models.EmailField(blank=True)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=8, choices=Currency.choices, default=Currency.USD)
    method = models.CharField(max_length=24, choices=Method.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    purpose = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    receipt_upload = models.FileField(upload_to=receipt_upload_path, blank=True, null=True)
    receipt_pdf = models.FileField(upload_to="receipts/pdf/", blank=True, null=True)
    payment_reference = models.CharField(max_length=80, unique=True, blank=True)
    risk_score = models.PositiveSmallIntegerField(default=0)
    suspicious_reason = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_donations")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "method"]),
            models.Index(fields=["public_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.public_id} {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = f"DN-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"
        if not self.payment_reference:
            self.payment_reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_card_payment(self) -> bool:
        return self.method in {self.Method.VISA, self.Method.MASTERCARD, self.Method.MIR}

    @property
    def amount_as_decimal(self) -> Decimal:
        return Decimal(self.amount)


class Transaction(models.Model):
    class Gateway(models.TextChoices):
        MANUAL_BANK = "manual_bank", _("Manual bank verification")
        CRYPTO = "crypto", _("Crypto transfer")
        CASH = "cash", _("Cash handover")

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="transactions")
    gateway = models.CharField(max_length=32, choices=Gateway.choices)
    external_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=16, choices=Donation.Status.choices, default=Donation.Status.PENDING)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    raw_payload = models.JSONField(default=dict, blank=True)
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["gateway", "status"]), models.Index(fields=["external_id"])]
