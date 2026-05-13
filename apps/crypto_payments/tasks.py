from celery import shared_task

from .models import CryptoPayment


@shared_task
def check_crypto_confirmations() -> int:
    # Integration point for BTC/ETH/TRON explorers. Kept deterministic for CI/dev.
    return CryptoPayment.objects.filter(status__in=[CryptoPayment.Status.WAITING_TX, CryptoPayment.Status.DETECTED]).count()
