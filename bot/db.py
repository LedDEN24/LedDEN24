"""Async-safe access to Django ORM for aiogram handlers.

Aiogram handlers run in an async event loop. Django ORM is synchronous, so any ORM
access must be executed in a thread via sync_to_async, otherwise Django raises
SynchronousOnlyOperation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import transaction

from apps.catalog.models import Category, Product
from apps.orders.checkout import update_order_workflow
from apps.orders.models import Order, OrderItem


@sync_to_async
def list_categories(limit: int = 30) -> List[Category]:
    return list(Category.objects.order_by("name")[: int(limit)])


@sync_to_async
def list_products(category_slug: str = "all", limit: int = 10) -> List[Product]:
    qs = Product.objects.filter(is_active=True).select_related("category").order_by("-created_at")
    if category_slug and category_slug != "all":
        qs = qs.filter(category__slug=category_slug)
    return list(qs[: int(limit)])


@sync_to_async
def list_hits(limit: int = 20) -> List[Product]:
    qs = Product.objects.filter(is_active=True, is_hit=True).select_related("category").order_by("-id")
    return list(qs[: int(limit)])


@sync_to_async
def list_news(limit: int = 20) -> List[Product]:
    qs = Product.objects.filter(is_active=True, is_new=True).select_related("category").order_by("-id")
    return list(qs[: int(limit)])


@sync_to_async
def search_products(q: str, limit: int = 10) -> List[Product]:
    q = (q or "").strip()
    if not q:
        return []
    qs = Product.objects.filter(is_active=True, title__icontains=q).select_related("category").order_by("-created_at")
    return list(qs[: int(limit)])


@sync_to_async
def get_product_by_slug(slug: str) -> Optional[Product]:
    return Product.objects.filter(slug=slug, is_active=True).first()


@sync_to_async
@transaction.atomic
def create_order_single_item(
    *,
    product_slug: str,
    qty: int,
    name: str,
    phone: str,
    address: str,
    comment: str,
    tg_user_id: str,
    tg_chat_id: str,
) -> int:
    """Create a simple cash order with a single product line.

    Returns created order id.
    """
    p = Product.objects.filter(slug=product_slug, is_active=True).first()
    if not p:
        raise ValueError("product_not_found")

    qty = max(int(qty or 1), 1)
    subtotal = int(p.price) * qty

    order = Order.objects.create(
        status="new",
        name=name,
        phone=phone,
        address=address or "",
        comment=comment or "",
        payment_method="cash",
        subtotal=subtotal,
        discount=0,
        delivery_price=0,
        total=subtotal,
        tg_user_id=str(tg_user_id),
        tg_chat_id=str(tg_chat_id),
    )

    OrderItem.objects.create(
        order=order,
        product=p,
        title=p.title,
        price=int(p.price),
        qty=qty,
    )

    return int(order.pk)


BOT_TO_WORKFLOW_STATUS = {
    "new": "new",
    "paid": "paid",
    "in_work": "confirmed",
    "assembling": "assembling",
    "delivering": "delivering",
    "done": "delivered",
    "delivered": "delivered",
    "canceled": "canceled",
    "refunded": "refunded",
}


@sync_to_async
def set_order_status(order_id: int, status: str) -> Optional[Order]:
    o = Order.objects.filter(pk=int(order_id)).first()
    if not o:
        return None
    workflow_status = BOT_TO_WORKFLOW_STATUS.get(status, status)
    o = update_order_workflow(o, workflow_status, comment="Статус обновлён из Telegram-бота")
    return Order.objects.select_related("delivery_slot").get(pk=o.pk)
