from django.db import models
from django.utils import timezone
from apps.catalog.models import Product


class Lead(models.Model):
    SOURCE_CHOICES = [("site", "site"), ("tg", "tg")]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="site")
    name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    tg_user_id = models.CharField(max_length=50, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    yookassa_payment_id = models.CharField(max_length=64, blank=True, default='')
    yookassa_status = models.CharField(max_length=32, blank=True, default='')
    yookassa_confirmation_url = models.URLField(blank=True, default='')

    def __str__(self):
        return f"{self.source} lead #{self.pk}"


class PromoCode(models.Model):
    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    def can_use(self):
        if not self.is_active:
            return False
        if self.valid_until and self.valid_until < timezone.now():
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True


class DeliveryOption(models.Model):
    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sort = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort", "id"]

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"


class DeliverySlot(models.Model):
    delivery_option = models.ForeignKey(DeliveryOption, on_delete=models.CASCADE, related_name="slots", null=True, blank=True)
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_active = models.BooleanField(default=True)
    capacity = models.PositiveSmallIntegerField(default=10)
    reserved_count = models.PositiveSmallIntegerField(default=0)
    same_day_only = models.BooleanField(default=False)

    class Meta:
        ordering = ["date", "time_from", "id"]
        unique_together = [("delivery_option", "date", "time_from", "time_to")]

    def __str__(self):
        option_name = self.delivery_option.name if self.delivery_option else "Любая доставка"
        return f"{option_name}: {self.label}"

    @property
    def is_available(self) -> bool:
        return self.is_active and self.reserved_count < self.capacity

    @property
    def remaining_capacity(self) -> int:
        return max(0, int(self.capacity) - int(self.reserved_count))

    @property
    def label(self) -> str:
        return f"{self.date:%d.%m.%Y} {self.time_from:%H:%M}–{self.time_to:%H:%M}"


class CartSession(models.Model):
    STATUS_CHOICES = [
        ("active", "active"),
        ("abandoned", "abandoned"),
        ("recovered", "recovered"),
        ("converted", "converted"),
    ]

    session_key = models.CharField(max_length=64, unique=True)
    tg_user_id = models.CharField(max_length=50, blank=True, default="")
    username = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    source = models.CharField(max_length=50, blank=True, default="site")
    utm_source = models.CharField(max_length=120, blank=True, default="")
    utm_medium = models.CharField(max_length=120, blank=True, default="")
    utm_campaign = models.CharField(max_length=120, blank=True, default="")
    last_activity_at = models.DateTimeField(auto_now=True)
    reminder_1_sent_at = models.DateTimeField(null=True, blank=True)
    reminder_2_sent_at = models.DateTimeField(null=True, blank=True)
    converted_order = models.ForeignKey("Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="converted_carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"CartSession({self.session_key}, {self.status})"


class CartItem(models.Model):
    cart_session = models.ForeignKey(CartSession, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("cart_session", "product")]

    def __str__(self):
        return f"{self.product} x{self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "new"),
        ("paid", "paid"),
        ("in_work", "in_work"),
        ("done", "done"),
        ("canceled", "canceled"),
    ]
    PAYMENT_CHOICES = [("cash", "cash"), ("online", "online")]
    STAGE_CHOICES = [
        ("new", "Новый"),
        ("in_progress", "В работе"),
        ("waiting_client", "Ждёт клиента"),
        ("agreed", "Согласован"),
        ("paid", "Оплачен"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменён"),
    ]
    WORKFLOW_STATUS_CHOICES = [
        ("new", "Новый"),
        ("pending_payment", "Ожидает оплату"),
        ("paid", "Оплачен"),
        ("confirmed", "Подтверждён"),
        ("assembling", "Собирается"),
        ("delivering", "В доставке"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменён"),
        ("refunded", "Возврат"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    tg_user_id = models.CharField(max_length=50, blank=True, default="")
    tg_chat_id = models.CharField(max_length=50, blank=True, default="")

    yookassa_payment_id = models.CharField(max_length=64, blank=True, default='')
    yookassa_status = models.CharField(max_length=32, blank=True, default='')
    yookassa_confirmation_url = models.URLField(blank=True, default='')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="new")
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS_CHOICES, default="new")
    manager_name = models.CharField(max_length=120, blank=True, default="")
    manager_comment = models.TextField(blank=True, default="")
    next_contact_at = models.DateTimeField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(default=0)
    customer_tag = models.CharField(max_length=80, blank=True, default="")

    source = models.CharField(max_length=50, blank=True, default="site")
    session_key = models.CharField(max_length=64, blank=True, default="")
    utm_source = models.CharField(max_length=120, blank=True, default="")
    utm_medium = models.CharField(max_length=120, blank=True, default="")
    utm_campaign = models.CharField(max_length=120, blank=True, default="")

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True, default="")
    comment = models.TextField(blank=True, default="")
    delivery_date = models.DateField(null=True, blank=True)

    delivery = models.ForeignKey(DeliveryOption, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_slot = models.ForeignKey(DeliverySlot, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    promo = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cash")
    payment_id = models.CharField(max_length=120, blank=True, default="")
    payment_url = models.URLField(blank=True, default="")

    subtotal = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    delivery_price = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order #{self.pk} ({self.workflow_status})"

    @property
    def payment_status(self):
        if self.payment_method != "online":
            return "not_required"
        if self.yookassa_status == "succeeded":
            return "paid"
        if self.yookassa_status == "canceled":
            return "failed"
        return self.yookassa_status or "pending"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=0)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order_id}: {self.title} x{self.qty}"

    @property
    def subtotal(self):
        return int(self.price) * int(self.qty)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=Order.WORKFLOW_STATUS_CHOICES)
    comment = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Order #{self.order_id} -> {self.status}"


class LeadEvent(models.Model):
    EVENT_CHOICES = [
        ("product_view", "product_view"),
        ("add_to_cart", "add_to_cart"),
        ("cart_remove", "cart_remove"),
        ("checkout_start", "checkout_start"),
        ("checkout_submit", "checkout_submit"),
        ("payment_success", "payment_success"),
        ("payment_fail", "payment_fail"),
        ("manager_contact", "manager_contact"),
    ]

    telegram_id = models.CharField(max_length=50, blank=True, default="")
    session_key = models.CharField(max_length=64, blank=True, default="")
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=50, blank=True, default="site")
    utm_source = models.CharField(max_length=120, blank=True, default="")
    utm_medium = models.CharField(max_length=120, blank=True, default="")
    utm_campaign = models.CharField(max_length=120, blank=True, default="")
    metadata_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} #{self.pk}"
