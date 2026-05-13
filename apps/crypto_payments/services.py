from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.donations.models import Donation
from apps.donations.services import approve_donation

from .models import CryptoPayment, CryptoWallet


def assign_wallet_for_donation(donation: Donation) -> CryptoPayment:
    currency = "USDT" if donation.method in {Donation.Method.USDT_ERC20, Donation.Method.USDT_TRC20} else donation.currency
    network = CryptoWallet.Network.TRC20 if donation.method == Donation.Method.USDT_TRC20 else CryptoWallet.Network.ERC20 if donation.method in {Donation.Method.ETH, Donation.Method.USDT_ERC20} else CryptoWallet.Network.BITCOIN
    wallet = CryptoWallet.objects.filter(currency=currency, network=network, is_active=True).first()
    if not wallet:
        raise CryptoWallet.DoesNotExist(f"No active wallet for {currency}/{network}")
    return CryptoPayment.objects.create(
        donation=donation,
        wallet=wallet,
        network=network,
        expected_amount=donation.amount,
        expires_at=timezone.now() + timedelta(hours=6),
    )


def mark_crypto_confirmed(payment: CryptoPayment, manager=None) -> CryptoPayment:
    payment.status = CryptoPayment.Status.CONFIRMED
    payment.confirmations = max(payment.confirmations, payment.wallet.min_confirmations)
    payment.save(update_fields=["status", "confirmations", "updated_at"])
    approve_donation(payment.donation, manager)
    return payment
