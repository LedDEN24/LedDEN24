import secrets
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def donation_receipt_path(instance, filename: str) -> str:
    return f"donations/{instance.donation.reference}/{filename}"


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

    reference = models.CharField(max_length=32, unique=True, editable=False)
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
    donor_name = models.CharField(max_length=160, blank=True)
    donor_email = models.EmailField(blank=True)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))])
    currency = models.CharField(max_length=8, default="USD")
    method = models.CharField(max_length=24, choices=Method.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    purpose = models.CharField(max_length=220)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    suspicious_score = models.PositiveSmallIntegerField(default=0)
    suspicious_reason = models.CharField(max_length=255, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_donations")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["method", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_reference() -> str:
        return f"DN-{timezone.now():%Y%m%d}-{secrets.token_hex(4).upper()}"

    def approve(self, reviewer) -> None:
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = ""
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])

    def reject(self, reviewer, reason: str) -> None:
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])

    def __str__(self) -> str:
        return f"{self.reference} {self.amount} {self.currency}"


class Transaction(models.Model):
    class Provider(models.TextChoices):
        MANUAL_CARD = "manual_card", _("Manual card verification")
        CRYPTO = "crypto", _("Crypto")
        CASH = "cash", _("Cash")

    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name="transaction")
    provider = models.CharField(max_length=32, choices=Provider.choices)
    provider_reference = models.CharField(max_length=160, blank=True)
    receipt = models.FileField(upload_to=donation_receipt_path, blank=True, null=True)
    screenshot = models.ImageField(upload_to=donation_receipt_path, blank=True, null=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.provider} for {self.donation.reference}"


class DonationAllocation(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="allocations")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="allocations")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("donation", "project")

    def __str__(self) -> str:
        return f"{self.amount} to {self.project}"
