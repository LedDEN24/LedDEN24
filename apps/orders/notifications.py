import os
from typing import Optional

import requests


WORKFLOW_STATUS_LABELS = {
    "new": "Новый",
    "pending_payment": "Ожидает оплату",
    "paid": "Оплачен",
    "confirmed": "Подтверждён",
    "assembling": "Собирается",
    "delivering": "В доставке",
    "delivered": "Доставлен",
    "canceled": "Отменён",
    "refunded": "Возврат",
}


WORKFLOW_STATUS_MESSAGES = {
    "new": "Заказ создан и скоро будет обработан.",
    "pending_payment": "Мы ждём подтверждение онлайн-оплаты.",
    "paid": "Оплата получена. Спасибо!",
    "confirmed": "Заказ подтверждён и передан в работу.",
    "assembling": "Флорист собирает ваш заказ.",
    "delivering": "Курьер уже в пути.",
    "delivered": "Заказ доставлен. Спасибо, что выбрали нас!",
    "canceled": "Заказ отменён. Если это ошибка, свяжитесь с нами.",
    "refunded": "Оформлен возврат средств.",
}


def _telegram_token() -> str:
    return os.getenv("TG_BOT_TOKEN", "").strip()


def _post_telegram(method: str, payload: dict) -> None:
    token = _telegram_token()
    if not token:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/{method}",
            json=payload,
            timeout=10,
        )
    except Exception:
        return


def notify_admins(text: str):
    admin_ids = [s.strip() for s in os.getenv("TG_ADMIN_IDS", "").split(",") if s.strip()]
    if not _telegram_token() or not admin_ids:
        return
    for chat_id in admin_ids:
        _post_telegram("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def workflow_status_label(status: str) -> str:
    return WORKFLOW_STATUS_LABELS.get((status or "").strip(), status or "—")


def build_customer_status_text(order, comment: str = "") -> str:
    label = workflow_status_label(getattr(order, "workflow_status", ""))
    lines = [
        f"Статус заказа №{order.pk}: {label}",
        WORKFLOW_STATUS_MESSAGES.get(getattr(order, "workflow_status", ""), ""),
    ]
    slot = getattr(order, "delivery_slot", None)
    if slot:
        lines.append(f"Слот доставки: {slot.label}")
    total = getattr(order, "total", None)
    if total:
        lines.append(f"Сумма заказа: {total} ₽")
    if comment:
        lines.append(f"Комментарий: {comment}")
    return "\n".join([line for line in lines if line])


def notify_customer_order_status(order, comment: str = "") -> bool:
    chat_id = str(getattr(order, "tg_chat_id", "") or "").strip()
    if not chat_id:
        return False
    _post_telegram(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": build_customer_status_text(order, comment=comment),
        },
    )
    return True
