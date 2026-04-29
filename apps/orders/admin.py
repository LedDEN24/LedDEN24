from collections import defaultdict
from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from .models import (
    CartItem,
    CartSession,
    DeliveryOption,
    DeliverySlot,
    Lead,
    LeadEvent,
    Order,
    OrderItem,
    OrderStatusHistory,
    PromoCode,
)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("source", "name", "phone", "tg_user_id", "product", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("name", "phone", "tg_user_id", "comment", "product__title")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title", "price", "qty")
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("status", "comment", "created_at")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "workflow_status", "status", "stage", "name", "phone", "total", "source", "payment_method")
    list_filter = ("workflow_status", "status", "stage", "payment_method", "source", "created_at")
    search_fields = ("id", "name", "phone", "address", "manager_name", "manager_comment")
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = (
        "subtotal", "discount", "delivery_price", "total", "payment_id", "payment_url", "created_at",
        "session_key", "utm_source", "utm_medium", "utm_campaign"
    )

    fieldsets = (
        (None, {"fields": ("created_at", "workflow_status", "status", "stage", "payment_method")}),
        ("Клиент", {"fields": ("name", "phone", "address", "comment", "customer_tag")}),
        ("Доставка", {"fields": ("delivery", "delivery_slot", "delivery_date")}),
        ("CRM", {"fields": ("manager_name", "manager_comment", "next_contact_at", "priority")}),
        ("Маркетинг", {"fields": ("source", "session_key", "utm_source", "utm_medium", "utm_campaign")}),
        ("Деньги", {"fields": ("subtotal", "discount", "delivery_price", "total", "promo")}),
        ("Онлайн-оплата", {"fields": ("yookassa_payment_id", "yookassa_status", "yookassa_confirmation_url", "payment_id", "payment_url")}),
    )

    def get_urls(self):
        return [
            path("orders-analytics/", self.admin_site.admin_view(orders_analytics_view), name="orders_analytics"),
        ] + super().get_urls()


@admin.register(CartSession)
class CartSessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "status", "phone", "source", "utm_source", "last_activity_at", "reminder_1_sent_at", "reminder_2_sent_at")
    list_filter = ("status", "source", "utm_source")
    search_fields = ("session_key", "phone", "username", "tg_user_id")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart_session", "product", "quantity", "price_snapshot", "updated_at")
    search_fields = ("cart_session__session_key", "product__title")


@admin.register(LeadEvent)
class LeadEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "product", "order", "source", "utm_source", "created_at")
    list_filter = ("event_type", "source", "utm_source", "created_at")
    search_fields = ("session_key", "utm_source", "utm_campaign", "product__title", "order__id")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "is_active", "valid_until", "usage_limit", "used_count")
    search_fields = ("code",)
    list_filter = ("is_active",)


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "sort")
    list_editable = ("price", "is_active", "sort")


@admin.register(DeliverySlot)
class DeliverySlotAdmin(admin.ModelAdmin):
    list_display = ("date", "time_from", "time_to", "delivery_option", "capacity", "reserved_count", "is_active")
    list_filter = ("date", "delivery_option", "is_active")
    search_fields = ("delivery_option__name",)


def orders_analytics_view(request):
    days = int(request.GET.get("days", 30))
    days = 7 if days <= 7 else 30 if days <= 30 else 90 if days <= 90 else 365
    date_from = timezone.now() - timedelta(days=days)
    qs = Order.objects.filter(created_at__gte=date_from)

    total_orders = qs.count()
    revenue = qs.aggregate(s=Sum("total"))["s"] or 0
    avg_check = int(revenue / total_orders) if total_orders else 0

    funnel = {
        "product_view": LeadEvent.objects.filter(created_at__gte=date_from, event_type="product_view").count(),
        "add_to_cart": LeadEvent.objects.filter(created_at__gte=date_from, event_type="add_to_cart").count(),
        "checkout_start": LeadEvent.objects.filter(created_at__gte=date_from, event_type="checkout_start").count(),
        "checkout_submit": LeadEvent.objects.filter(created_at__gte=date_from, event_type="checkout_submit").count(),
        "paid_orders": qs.filter(status="paid").count(),
    }

    source_stats = defaultdict(lambda: {"orders": 0, "revenue": 0})
    for order in qs:
        key = order.utm_source or order.source or "unknown"
        source_stats[key]["orders"] += 1
        source_stats[key]["revenue"] += int(order.total)

    product_stats = defaultdict(lambda: {"title": "", "qty": 0, "revenue": 0})
    for item in OrderItem.objects.filter(order__created_at__gte=date_from).select_related("product"):
        key = item.product_id
        product_stats[key]["title"] = item.title
        product_stats[key]["qty"] += int(item.qty)
        product_stats[key]["revenue"] += int(item.price) * int(item.qty)

    context = {
        "days": days,
        "total_orders": total_orders,
        "revenue": revenue,
        "avg_check": avg_check,
        "top_products": sorted(product_stats.values(), key=lambda x: x["revenue"], reverse=True)[:10],
        "source_stats": sorted(source_stats.items(), key=lambda x: x[1]["revenue"], reverse=True),
        "funnel": funnel,
        "abandoned_carts": CartSession.objects.filter(status="abandoned").count(),
    }
    return render(request, "admin/orders_analytics.html", context)
