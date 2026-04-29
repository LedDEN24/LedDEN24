import json

from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.catalog.models import Product
from .cart import Cart
from .checkout import apply_payment_status, create_order_from_cart
from .models import DeliveryOption, DeliverySlot, Order
from .notifications import notify_admins
from .security import is_valid_yookassa_request
from .tracking import sync_cart_session, track_event
from .yookassa_gateway import create_payment_for_order, fetch_payment_status


def _safe_qty(value, default=1):
    try:
        qty = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(qty, 99))


def _wants_json(request) -> bool:
    requested_with = request.headers.get("X-Requested-With", "")
    accept = request.headers.get("Accept", "")
    return requested_with.lower() == "fetch" or "application/json" in accept.lower()


def _cart_state(cart: Cart) -> dict:
    lines = cart.lines()
    return {
        "cart_count": len(cart),
        "cart_subtotal": int(cart.subtotal),
        "items": {
            line.product.slug: {
                "qty": int(line.qty),
                "unit_price": int(line.product.price),
                "line_total": int(line.line_total),
                "title": line.product.title,
            }
            for line in lines
        },
    }


def _cart_json_response(cart: Cart, *, message: str = "", action: str = "", product: Product | None = None):
    payload = {"ok": True, "message": message, "action": action, **_cart_state(cart)}
    if product:
        payload["product"] = {"slug": product.slug, "title": product.title}
    return JsonResponse(payload)


def _get_owned_order_or_404(request, pk: int) -> Order:
    order = get_object_or_404(Order, pk=pk)
    session_key = request.session.session_key or ""
    if not session_key or order.session_key != session_key:
        raise Http404("Order not found")
    return order


def cart_detail(request):
    cart = Cart(request)
    sync_cart_session(request, cart)
    return render(request, "orders/cart.html", {"cart": cart, "lines": cart.lines()})


@require_POST
def cart_add(request, slug):
    cart = Cart(request)
    qty = _safe_qty(request.POST.get("qty", 1))
    cart.add(slug, qty=qty)
    sync_cart_session(request, cart)
    product = Product.objects.filter(slug=slug).first()
    if product:
        track_event(request, event_type="add_to_cart", product=product, metadata={"qty": qty})
    if _wants_json(request):
        return _cart_json_response(
            cart,
            message="Товар добавлен в корзину",
            action="add",
            product=product,
        )
    messages.success(request, "Добавлено в корзину")
    return redirect(request.META.get("HTTP_REFERER") or "cart_detail")


@require_POST
def cart_remove(request, slug):
    cart = Cart(request)
    product = Product.objects.filter(slug=slug).first()
    cart.remove(slug)
    sync_cart_session(request, cart)
    if product:
        track_event(request, event_type="cart_remove", product=product)
    if _wants_json(request):
        return _cart_json_response(
            cart,
            message="Товар удален из корзины",
            action="remove",
            product=product,
        )
    return redirect("cart_detail")


@require_POST
def cart_update(request):
    cart = Cart(request)
    for key, value in request.POST.items():
        if key.startswith("qty_"):
            slug = key.replace("qty_", "")
            try:
                cart.set_qty(slug, _safe_qty(value))
            except Exception:
                continue
    sync_cart_session(request, cart)
    if _wants_json(request):
        return _cart_json_response(
            cart,
            message="Корзина обновлена",
            action="update",
        )
    return redirect("cart_detail")


def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    if not lines:
        return redirect("cart_detail")

    delivery_options = DeliveryOption.objects.filter(is_active=True).order_by("sort", "id")
    delivery_slots = DeliverySlot.objects.filter(is_active=True).select_related("delivery_option").order_by("date", "time_from", "id")

    if request.method == "POST":
        cart_session = sync_cart_session(request, cart)
        try:
            order = create_order_from_cart(
                cart=cart,
                name=request.POST.get("name", "").strip(),
                phone=request.POST.get("phone", "").strip(),
                address=request.POST.get("address", "").strip(),
                comment=request.POST.get("comment", "").strip(),
                delivery_method=request.POST.get("delivery_method", "courier").strip(),
                coupon_code=request.POST.get("coupon", "").strip(),
                delivery_slot_id=request.POST.get("delivery_slot", "").strip(),
                payment_method=request.POST.get("payment_method", "cash").strip(),
                source=cart_session.source,
                session_key=cart_session.session_key,
                utm_source=cart_session.utm_source,
                utm_medium=cart_session.utm_medium,
                utm_campaign=cart_session.utm_campaign,
            )
        except Exception as exc:
            messages.error(request, str(exc))
            return render(
                request,
                "orders/checkout.html",
                {
                    "cart": cart,
                    "lines": lines,
                    "delivery_options": delivery_options,
                    "delivery_slots": delivery_slots,
                    "cart_count": len(cart),
                },
            )

        cart_session.phone = order.phone
        cart_session.status = "converted"
        cart_session.converted_order = order
        cart_session.save(update_fields=["phone", "status", "converted_order", "updated_at"])
        track_event(request, event_type="checkout_submit", order=order, metadata={"total": order.total})

        if order.payment_method == "online":
            return_url = request.build_absolute_uri(reverse("yookassa_return", args=[order.pk]))
            url = create_payment_for_order(order, return_url=return_url)
            return redirect(url)
        return redirect("order_success", pk=order.pk)

    track_event(request, event_type="checkout_start", metadata={"subtotal": cart.subtotal})
    sync_cart_session(request, cart)
    return render(
        request,
        "orders/checkout.html",
        {
            "cart": cart,
            "lines": lines,
            "delivery_options": delivery_options,
            "delivery_slots": delivery_slots,
            "cart_count": len(cart),
        },
    )


def order_success(request, pk: int):
    order = _get_owned_order_or_404(request, pk)
    if order.payment_method == "online" and order.yookassa_payment_id and order.payment_status != "paid":
        try:
            status = fetch_payment_status(order.yookassa_payment_id)
            order = apply_payment_status(order, status)
        except Exception:
            pass
    return render(request, "orders/success.html", {"order": order})


def my_orders(request):
    session_key = request.session.session_key or ""
    orders = Order.objects.filter(session_key=session_key).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    if not is_valid_yookassa_request(request):
        return HttpResponseBadRequest("forbidden")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("bad json")

    event = data.get("event", "")
    obj = data.get("object") or {}
    payment_id = obj.get("id") or ""
    metadata = obj.get("metadata") or {}
    order_id = metadata.get("order_id")

    order = None
    if payment_id:
        order = Order.objects.filter(yookassa_payment_id=payment_id).first()
    if not order and order_id:
        order = Order.objects.filter(pk=int(order_id)).first()
    if not order:
        return JsonResponse({"ok": True})

    try:
        status = fetch_payment_status(order.yookassa_payment_id)
    except Exception:
        status = obj.get("status", "") or ""

    if event == "payment.succeeded" or status == "succeeded":
        order = apply_payment_status(order, "succeeded")
        track_event(request, event_type="payment_success", order=order, metadata={"status": "succeeded"})
        notify_admins(f"<b>Оплата получена ✅</b>\nЗаказ #{order.pk} на сумму {order.total} ₽")
    elif event == "payment.canceled" or status == "canceled":
        order = apply_payment_status(order, "canceled")
        track_event(request, event_type="payment_fail", order=order, metadata={"status": "canceled"})
    else:
        order = apply_payment_status(order, status)

    return JsonResponse({"ok": True})


def order_failed(request, pk: int):
    order = _get_owned_order_or_404(request, pk)
    return render(request, "orders/failed.html", {"order": order})


def yookassa_return(request, pk: int):
    order = _get_owned_order_or_404(request, pk)
    if order.yookassa_payment_id:
        try:
            status = fetch_payment_status(order.yookassa_payment_id)
            order = apply_payment_status(order, status)
            if status == "succeeded":
                return redirect("order_success", pk=order.pk)
            if status == "canceled":
                return redirect("order_failed", pk=order.pk)
        except Exception:
            pass
    return redirect("order_success", pk=order.pk)
