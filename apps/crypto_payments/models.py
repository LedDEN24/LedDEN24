from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class CryptoWallet(models.Model):
    class Currency(models.TextChoices):
        BTC = "BTC", "Bitcoin"
        ETH = "ETH", "Ethereum"
        USDT = "USDT", "USDT"

    class Network(models.TextChoices):
        BITCOIN = "bitcoin", "Bitcoin"
        ERC20 = "erc20", "ERC20"
        TRC20 = "trc20", "TRC20"

    currency = models.CharField(max_length=8, choices=Currency.choices)
    network = models.CharField(max_length=16, choices=Network.choices)
    address = models.CharField(max_length=160, unique=True)
    label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    min_confirmations = models.PositiveSmallIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["currency", "network"]
        unique_together = ("currency", "network", "address")

    def __str__(self) -> str:
        return f"{self.currency} {self.network}"


class CryptoPayment(models.Model):
    class Status(models.TextChoices):
        WAITING_TX = "waiting_tx", _("Waiting transaction")
        DETECTED = "detected", _("Detected")
        CONFIRMED = "confirmed", _("Confirmed")
        FAILED = "failed", _("Failed")

    donation = models.OneToOneField("donations.Donation", on_delete=models.CASCADE, related_name="crypto_payment")
    wallet = models.ForeignKey(CryptoWallet, on_delete=models.PROTECT, related_name="payments")
    tx_hash = models.CharField(max_length=160, blank=True)
    network = models.CharField(max_length=16)
    expected_amount = models.DecimalField(max_digits=20, decimal_places=8)
    received_amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    confirmations = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.WAITING_TX)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["tx_hash"]), models.Index(fields=["status"])]
