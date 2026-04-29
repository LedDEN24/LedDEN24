from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from .cart import Cart
from .models import DeliveryOption, DeliverySlot, Order, OrderItem, OrderStatusHistory, PromoCode
from .notifications import notify_admins, notify_customer_order_status


@dataclass
class Totals:
    subtotal: int
    discount: int
    delivery_price: int
    total: int
    promo: Optional[PromoCode] = None


MAX_ITEM_QTY = 99
VALID_PAYMENT_METHODS = {"cash", "online"}


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_payment_method(value: str) -> str:
    value = (value or "cash").strip().lower()
    if value not in VALID_PAYMENT_METHODS:
        raise ValidationError("Некорректный способ оплаты")
    return value


def resolve_delivery_option(delivery_value: str) -> Optional[DeliveryOption]:
    delivery_value = (delivery_value or "").strip()
    if not delivery_value:
        return None

    if delivery_value.isdigit():
        return DeliveryOption.objects.filter(id=int(delivery_value), is_active=True).first()

    normalized = delivery_value.lower()
    if normalized == "pickup":
        return DeliveryOption.objects.filter(is_active=True, price=0).order_by("sort", "id").first()
    if normalized == "courier":
        return DeliveryOption.objects.filter(is_active=True).exclude(price=0).order_by("sort", "id").first()

    return DeliveryOption.objects.filter(name__iexact=delivery_value, is_active=True).order_by("sort", "id").first()


def calc_delivery(delivery_method: str) -> tuple[int, Optional[DeliveryOption]]:
    delivery = resolve_delivery_option(delivery_method)
    if delivery:
        return int(delivery.price), delivery
    if (delivery_method or "").strip().lower() == "pickup":
        return 0, None
    return 350, None


def validate_checkout_payload(*, name: str, phone: str, payment_method: str, lines) -> str:
    if not (name or "").strip():
        raise ValidationError("Укажите имя")
    if not (phone or "").strip():
        raise ValidationError("Укажите телефон")
    payment_method = normalize_payment_method(payment_method)
    if not lines:
        raise ValidationError("Корзина пуста")
    for line in lines:
        qty = _safe_int(line.qty, 0)
        if qty <= 0 or qty > MAX_ITEM_QTY:
            raise ValidationError(f"Некорректное количество для {line.product.title}")
    return payment_method


def ensure_stock_available(lines) -> None:
    for line in lines:
        product = line.product
        qty = _safe_int(line.qty, 0)
        if not product.in_stock or _safe_int(product.quantity, 0) < qty:
            raise ValidationError(f"Недостаточно остатка для товара: {product.title}")


def apply_promo(code: str, subtotal: int) -> tuple[int, Optional[PromoCode]]:
    code = (code or "").strip().upper()
    if not code:
        return 0, None
    p = PromoCode.objects.filter(code=code, is_active=True).first()
    if not p or not p.can_use():
        return 0, None
    discount = int(subtotal * (int(p.discount_percent) / 100))
    return max(0, min(discount, subtotal)), p


@transaction.atomic
def reserve_delivery_slot(slot_id: str, delivery: Optional[DeliveryOption]) -> Optional[DeliverySlot]:
    slot_id = (slot_id or "").strip()
    if not slot_id:
        return None
    if not slot_id.isdigit():
        raise ValidationError("Некорректный слот доставки")
    slot = DeliverySlot.objects.select_for_update().filter(pk=int(slot_id), is_active=True).select_related("delivery_option").first()
    if not slot:
        raise ValidationError("Слот доставки не найден")
    if delivery and slot.delivery_option_id and slot.delivery_option_id != delivery.id:
        raise ValidationError("Слот не относится к выбранному способу доставки")
    if not slot.is_available:
        raise ValidationError("Выбранный слот доставки уже заполнен")
    slot.reserved_count = F("reserved_count") + 1
    slot.save(update_fields=["reserved_count"])
    slot.refresh_from_db(fields=["reserved_count"])
    return slot


@transaction.atomic
def release_delivery_slot(order: Order) -> None:
    if not order.delivery_slot_id:
        return
    slot = DeliverySlot.objects.select_for_update().filter(pk=order.delivery_slot_id).first()
    if not slot or slot.reserved_count <= 0:
        return
    slot.reserved_count = F("reserved_count") - 1
    slot.save(update_fields=["reserved_count"])


@transaction.atomic
def update_order_workflow(order: Order, workflow_status: str, comment: str = "") -> Order:
    order = Order.objects.select_for_update().select_related("delivery_slot").get(pk=order.pk)
    changed = order.workflow_status != workflow_status
    order.workflow_status = workflow_status
    if workflow_status == "paid":
        order.status = "paid"
        order.stage = "paid"
    elif workflow_status in {"confirmed", "assembling", "delivering"}:
        order.status = "in_work"
        order.stage = "in_progress"
    elif workflow_status == "delivered":
        order.status = "done"
        order.stage = "completed"
    elif workflow_status == "canceled":
        order.status = "canceled"
        order.stage = "cancelled"
    order.save(update_fields=["workflow_status", "status", "stage"])
    if changed or comment:
        OrderStatusHistory.objects.create(order=order, status=workflow_status, comment=comment)
    if changed:
        notify_customer_order_status(order, comment=comment)
    return order


@transaction.atomic
def create_order_from_cart(*, cart: Cart, name: str, phone: str, address: str, comment: str, delivery_method: str, delivery_slot_id: str = "", coupon_code: str, payment_method: str, source: str = "site", session_key: str = "", utm_source: str = "", utm_medium: str = "", utm_campaign: str = "", tg_user_id: str = "", tg_chat_id: str = "") -> Order:
    lines = cart.lines()
    payment_method = validate_checkout_payload(name=name, phone=phone, payment_method=payment_method, lines=lines)
    ensure_stock_available(lines)

    subtotal = sum(l.line_total for l in lines)
    delivery_price, delivery = calc_delivery(delivery_method)
    discount, promo = apply_promo(coupon_code, subtotal)
    total = max(0, subtotal - discount + delivery_price)
    slot = reserve_delivery_slot(delivery_slot_id, delivery) if delivery_slot_id else None

    workflow_status = "pending_payment" if payment_method == "online" else "confirmed"
    stage = "new" if payment_method == "online" else "in_progress"

    order = Order.objects.create(
        name=name, phone=phone, address=address, comment=comment,
        subtotal=subtotal, discount=discount, delivery_price=delivery_price, total=total,
        promo=promo, delivery=delivery, delivery_slot=slot, payment_method=payment_method, status="new", stage=stage,
        workflow_status=workflow_status,
        source=source, session_key=session_key, utm_source=utm_source, utm_medium=utm_medium, utm_campaign=utm_campaign,
        tg_user_id=tg_user_id, tg_chat_id=tg_chat_id,
    )

    for l in lines:
        OrderItem.objects.create(order=order, product=l.product, title=l.product.title, price=int(l.product.price), qty=int(l.qty))

    OrderStatusHistory.objects.create(order=order, status=workflow_status, comment="Заказ создан")

    if promo:
        PromoCode.objects.filter(pk=promo.pk).update(used_count=F("used_count") + 1)

    if payment_method == "cash":
        commit_order_inventory(order)

    notify_admins(_format_order(order))
    cart.clear()
    return order


@transaction.atomic
def commit_order_inventory(order: Order) -> None:
    order = Order.objects.select_for_update().prefetch_related("items__product").get(pk=order.pk)
    for item in order.items.all():
        product = item.product
        product = type(product).objects.select_for_update().get(pk=product.pk)
        if _safe_int(product.quantity, 0) < _safe_int(item.qty, 0):
            raise ValidationError(f"Недостаточно остатка для товара: {product.title}")
        product.quantity = max(0, _safe_int(product.quantity, 0) - _safe_int(item.qty, 0))
        if product.quantity == 0:
            product.in_stock = False
        product.save(update_fields=["quantity", "in_stock"])


@transaction.atomic
def apply_payment_status(order: Order, status: str) -> Order:
    order = Order.objects.select_for_update().get(pk=order.pk)
    previous_status = order.yookassa_status or ""
    order.yookassa_status = status or ""
    order.save(update_fields=["yookassa_status"])

    if status == "succeeded":
        if previous_status != "succeeded":
            commit_order_inventory(order)
        return update_order_workflow(order, "paid", "Онлайн-оплата подтверждена")

    if status == "canceled":
        release_delivery_slot(order)
        return update_order_workflow(order, "canceled", "Онлайн-оплата отменена")

    return order


def _format_order(order: Order) -> str:
    items_txt = "\n".join([f"• {it.title} × {it.qty} = {it.price * it.qty} ₽" for it in order.items.all()]) or "-"
    slot_txt = order.delivery_slot.label if order.delivery_slot else "-"
    return (
        f"<b>Новый заказ #{order.pk}</b>\n"
        f"Имя: {order.name}\nТел: {order.phone}\n"
        f"Доставка: {order.delivery_price} ₽\nАдрес: {order.address or '-'}\n"
        f"Слот: {slot_txt}\n"
        f"Сумма: {order.total} ₽ (скидка {order.discount} ₽)\n"
        f"Источник: {order.source or '-'} / {order.utm_source or '-'}\n\n"
        f"{items_txt}\n\nКомментарий: {order.comment or '-'}"
    )
