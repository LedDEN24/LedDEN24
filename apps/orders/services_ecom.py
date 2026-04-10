from __future__ import annotations
import os
import requests
from dataclasses import dataclass
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Product
from apps.orders.cart import Cart
from apps.orders.models import Order, OrderItem, PromoCode, DeliveryOption


def _tg_notify(text: str):
    token = os.getenv("TG_BOT_TOKEN", "").strip()
    admin_ids = [s.strip() for s in os.getenv("TG_ADMIN_IDS","").split(",") if s.strip()]
    if not token or not admin_ids:
        return
    for aid in admin_ids:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": aid, "text": text},
                timeout=10,
            )
        except Exception:
            pass


def find_promo(code: str) -> Optional[PromoCode]:
    code = (code or "").strip().upper()
    if not code:
        return None
    promo = PromoCode.objects.filter(code=code, is_active=True).first()
    if not promo:
        return None
    if promo.valid_until and promo.valid_until < timezone.now():
        return None
    if promo.usage_limit is not None and promo.used_count >= promo.usage_limit:
        return None
    return promo


@transaction.atomic
def create_order_from_cart(
    cart: Cart,
    name: str,
    phone: str,
    address: str = "",
    comment: str = "",
    delivery_id: Optional[int] = None,
    promo_code: str = "",
    payment_method: str = "cash",
):
    items = list(cart.iter_lines())
    if not items:
        raise ValueError("Cart is empty")

    delivery = DeliveryOption.objects.filter(id=delivery_id, is_active=True).first() if delivery_id else None
    promo = find_promo(promo_code)

    subtotal = cart.total
    discount = 0
    if promo and promo.discount_percent:
        discount = int(subtotal * promo.discount_percent / 100)

    delivery_price = int(delivery.price) if delivery else 0
    total = max(0, subtotal - discount) + delivery_price

    order = Order.objects.create(
        name=name,
        phone=phone,
        address=address,
        comment=comment,
        delivery=delivery,
        promo=promo,
        payment_method=payment_method,
        subtotal=subtotal,
        discount=discount,
        delivery_price=delivery_price,
        total=total,
    )

    for line in items:
        OrderItem.objects.create(
            order=order,
            product=line.product,
            title=line.product.title,
            price=line.product.price,
            qty=line.qty,
        )

    if promo:
        PromoCode.objects.filter(id=promo.id).update(used_count=promo.used_count + 1)

    _tg_notify(_format_order_text(order))
    cart.clear()
    return order


def _format_order_text(order: Order) -> str:
    lines = [f"🧾 Новый заказ #{order.id}",
             f"👤 {order.name}",
             f"☎️ {order.phone}"]
    if order.address:
        lines.append(f"📍 {order.address}")
    if order.delivery:
        lines.append(f"🚚 Доставка: {order.delivery.name} ({order.delivery_price} ₽)")
    if order.promo:
        lines.append(f"🏷 Промокод: {order.promo.code} (-{order.promo.discount_percent}%)")
    lines.append("—")
    for it in order.items.all():
        lines.append(f"• {it.title} ×{it.qty} — {it.subtotal} ₽")
    lines.append("—")
    lines.append(f"Итого: {order.total} ₽ ({order.payment_method})")
    if order.comment:
        lines.append(f"💬 {order.comment}")
    return "\n".join(lines)
