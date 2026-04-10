import os
from datetime import date, time, timedelta
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.orders.cart import CART_SESSION_KEY
from apps.orders.checkout import apply_payment_status, create_order_from_cart
from apps.orders.models import DeliveryOption, DeliverySlot, Order, OrderStatusHistory


class EcommerceFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="bukety")
        self.product = Product.objects.create(
            category=self.category,
            title="Розы",
            slug="roses",
            price=500,
            quantity=5,
            in_stock=True,
            is_active=True,
        )
        self.delivery = DeliveryOption.objects.create(name="Курьер", price=350, is_active=True, sort=1)
        self.slot = DeliverySlot.objects.create(
            delivery_option=self.delivery,
            date=date.today() + timedelta(days=1),
            time_from=time(12, 0),
            time_to=time(14, 0),
            capacity=2,
            reserved_count=0,
            is_active=True,
        )

    def _build_cart_request(self):
        client = Client()
        session = client.session
        session[CART_SESSION_KEY] = {self.product.slug: 2}
        session.save()
        request = client.get(reverse("checkout")).wsgi_request
        request.session = client.session
        return client, request

    def test_create_order_online_keeps_stock_until_payment(self):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="online",
            session_key=client.session.session_key,
        )
        self.product.refresh_from_db()
        self.slot.refresh_from_db()
        self.assertEqual(order.total, 1350)
        self.assertEqual(self.product.quantity, 5)
        self.assertEqual(order.workflow_status, "pending_payment")
        self.assertEqual(self.slot.reserved_count, 1)

        apply_payment_status(order, "succeeded")
        self.product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.workflow_status, "paid")

    def test_cash_order_reduces_stock_immediately(self):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="cash",
            session_key=client.session.session_key,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)
        self.assertEqual(order.workflow_status, "confirmed")

    def test_order_pages_are_private_per_session(self):
        owner = Client()
        session = owner.session
        session[CART_SESSION_KEY] = {self.product.slug: 1}
        session.save()
        response = owner.post(
            reverse("checkout"),
            {
                "name": "Иван",
                "phone": "79990000000",
                "address": "Тест",
                "comment": "",
                "delivery_method": str(self.delivery.id),
                "delivery_slot": str(self.slot.id),
                "payment_method": "cash",
            },
        )
        order = Order.objects.latest("id")
        self.assertEqual(response.status_code, 302)

        stranger = Client()
        stranger_response = stranger.get(reverse("order_success", args=[order.pk]))
        self.assertEqual(stranger_response.status_code, 404)

        owner_response = owner.get(reverse("order_success", args=[order.pk]))
        self.assertEqual(owner_response.status_code, 200)

    def test_cart_add_invalid_qty_is_safely_normalized(self):
        client = Client()
        response = client.post(reverse("cart_add", args=[self.product.slug]), {"qty": "oops"})
        self.assertEqual(response.status_code, 302)
        session = client.session
        self.assertEqual(session[CART_SESSION_KEY][self.product.slug], 1)

    @patch("apps.orders.views.fetch_payment_status", return_value="succeeded")
    def test_success_page_applies_payment_and_commits_stock(self, _mock_status):
        owner = Client()
        session = owner.session
        session[CART_SESSION_KEY] = {self.product.slug: 1}
        session.save()

        with patch("apps.orders.views.create_payment_for_order", return_value="https://example.com/pay"):
            response = owner.post(
                reverse("checkout"),
                {
                    "name": "Иван",
                    "phone": "79990000000",
                    "address": "Тест",
                    "comment": "",
                    "delivery_method": str(self.delivery.id),
                    "delivery_slot": str(self.slot.id),
                    "payment_method": "online",
                },
            )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.latest("id")
        order.yookassa_payment_id = "pay_1"
        order.save(update_fields=["yookassa_payment_id"])

        page = owner.get(reverse("order_success", args=[order.pk]))
        self.assertEqual(page.status_code, 200)
        order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.workflow_status, "paid")
        self.assertEqual(self.product.quantity, 4)

    def test_slot_is_released_when_online_payment_is_canceled(self):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="online",
            session_key=client.session.session_key,
        )
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.reserved_count, 1)

        apply_payment_status(order, "canceled")
        order.refresh_from_db()
        self.slot.refresh_from_db()
        self.assertEqual(order.workflow_status, "canceled")
        self.assertEqual(self.slot.reserved_count, 0)

    def test_status_history_is_written(self):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="online",
            session_key=client.session.session_key,
        )
        apply_payment_status(order, "succeeded")

        statuses = list(OrderStatusHistory.objects.filter(order=order).values_list("status", flat=True))
        self.assertEqual(statuses, ["pending_payment", "paid"])


    @patch.dict(os.environ, {"TG_BOT_TOKEN": "token"}, clear=False)
    @patch("apps.orders.notifications.requests.post")
    def test_customer_receives_telegram_notification_on_status_change(self, mock_post):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="cash",
            session_key=client.session.session_key,
            tg_chat_id="123456",
        )

        from apps.orders.checkout import update_order_workflow

        update_order_workflow(order, "delivering", "Курьер выехал")

        self.assertTrue(mock_post.called)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["chat_id"], "123456")
        self.assertIn("В доставке", payload["text"])
        self.assertIn("Курьер выехал", payload["text"])

    def test_bot_status_mapping_updates_workflow_status(self):
        client, request = self._build_cart_request()
        from apps.orders.cart import Cart
        from bot.db import set_order_status
        from asgiref.sync import async_to_sync

        order = create_order_from_cart(
            cart=Cart(request),
            name="Иван",
            phone="79990000000",
            address="Тест",
            comment="",
            delivery_method=str(self.delivery.id),
            delivery_slot_id=str(self.slot.id),
            coupon_code="",
            payment_method="cash",
            session_key=client.session.session_key,
        )

        updated = async_to_sync(set_order_status)(order.pk, "done")
        order.refresh_from_db()
        self.assertEqual(updated.workflow_status, "delivered")
        self.assertEqual(order.workflow_status, "delivered")
