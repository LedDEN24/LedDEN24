from __future__ import annotations

import os
import uuid
from decimal import Decimal

from yookassa import Configuration, Payment

from .models import Order


def _configure():
    shop_id = os.getenv("YOOKASSA_SHOP_ID", "").strip()
    secret = os.getenv("YOOKASSA_SECRET_KEY", "").strip()
    if not shop_id or not secret:
        raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY не заданы в .env")
    Configuration.account_id = shop_id
    Configuration.secret_key = secret


def create_payment_for_order(order: Order, *, return_url: str) -> str:
    """Создает 'Умный платеж' (redirect) и возвращает confirmation_url."""
    _configure()

    idempotence_key = str(uuid.uuid4())
    amount_value = f"{Decimal(order.total):.2f}"

    payment = Payment.create(
        {
            "amount": {"value": amount_value, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Order #{order.pk}",
            "metadata": {"order_id": str(order.pk)},
        },
        idempotence_key,
    )

    order.yookassa_payment_id = payment.id or ""
    order.yookassa_status = getattr(payment, "status", "") or ""
    order.yookassa_confirmation_url = getattr(payment.confirmation, "confirmation_url", "") or ""
    order.save(update_fields=["yookassa_payment_id", "yookassa_status", "yookassa_confirmation_url"])

    return order.yookassa_confirmation_url


def fetch_payment_status(payment_id: str) -> str:
    _configure()
    p = Payment.find_one(payment_id)
    return getattr(p, "status", "") or ""
