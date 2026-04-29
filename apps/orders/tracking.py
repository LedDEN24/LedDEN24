from __future__ import annotations

from django.utils import timezone

from .models import CartItem, CartSession, LeadEvent


def get_or_create_cart_session(request) -> CartSession:
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_session, _ = CartSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            "source": "site",
            "utm_source": request.GET.get("utm_source", "") or request.session.get("utm_source", ""),
            "utm_medium": request.GET.get("utm_medium", "") or request.session.get("utm_medium", ""),
            "utm_campaign": request.GET.get("utm_campaign", "") or request.session.get("utm_campaign", ""),
        },
    )
    for field in ("utm_source", "utm_medium", "utm_campaign"):
        if request.GET.get(field):
            request.session[field] = request.GET.get(field)
            setattr(cart_session, field, request.GET.get(field))
    cart_session.last_activity_at = timezone.now()
    cart_session.save()
    return cart_session


def sync_cart_session(request, cart) -> CartSession:
    cart_session = get_or_create_cart_session(request)
    existing = {item.product_id: item for item in cart_session.items.all()}
    current_products = set()
    for line in cart.lines():
        current_products.add(line.product.id)
        item = existing.get(line.product.id)
        if item:
            if item.quantity != int(line.qty) or item.price_snapshot != int(line.product.price):
                item.quantity = int(line.qty)
                item.price_snapshot = int(line.product.price)
                item.save(update_fields=["quantity", "price_snapshot", "updated_at"])
        else:
            CartItem.objects.create(
                cart_session=cart_session,
                product=line.product,
                quantity=int(line.qty),
                price_snapshot=int(line.product.price),
            )
    for product_id, item in existing.items():
        if product_id not in current_products:
            item.delete()
    cart_session.last_activity_at = timezone.now()
    cart_session.status = "active" if current_products else cart_session.status
    cart_session.save(update_fields=["last_activity_at", "status", "updated_at"])
    return cart_session


def track_event(request, *, event_type: str, product=None, order=None, metadata: dict | None = None) -> LeadEvent:
    cart_session = get_or_create_cart_session(request)
    return LeadEvent.objects.create(
        telegram_id="",
        session_key=cart_session.session_key,
        event_type=event_type,
        product=product,
        order=order,
        source=cart_session.source,
        utm_source=cart_session.utm_source,
        utm_medium=cart_session.utm_medium,
        utm_campaign=cart_session.utm_campaign,
        metadata_json=metadata or {},
    )
