from django.db import models
from django.utils.translation import gettext_lazy as _


class CryptoWallet(models.Model):
    class Network(models.TextChoices):
        BTC = "btc", "Bitcoin"
        ETH = "eth", "Ethereum"
        TRC20 = "trc20", "TRON TRC20"
        ERC20 = "erc20", "Ethereum ERC20"

    title = models.CharField(max_length=120)
    network = models.CharField(max_length=16, choices=Network.choices)
    currency = models.CharField(max_length=16)
    address = models.CharField(max_length=160, unique=True)
    qr_code = models.ImageField(upload_to="crypto-wallets/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["currency", "network"]

    def __str__(self) -> str:
        return f"{self.currency} {self.network}: {self.address[:10]}..."


class CryptoPayment(models.Model):
    class Status(models.TextChoices):
        WAITING = "waiting", _("Waiting for transfer")
        DETECTED = "detected", _("Transfer detected")
        CONFIRMED = "confirmed", _("Confirmed")
        FAILED = "failed", _("Failed")

    donation = models.OneToOneField("donations.Donation", on_delete=models.CASCADE, related_name="crypto_payment")
    wallet = models.ForeignKey(CryptoWallet, on_delete=models.PROTECT, related_name="payments")
    tx_hash = models.CharField(max_length=180, blank=True)
    expected_amount = models.DecimalField(max_digits=24, decimal_places=8)
    received_amount = models.DecimalField(max_digits=24, decimal_places=8, blank=True, null=True)
    confirmations = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["status", "tx_hash"])]

    def __str__(self) -> str:
        return f"{self.donation.reference} {self.wallet.currency}"
