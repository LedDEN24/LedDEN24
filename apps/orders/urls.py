from django.urls import path
from . import views

urlpatterns = [
    path('payments/yookassa/webhook/', views.yookassa_webhook, name='yookassa_webhook'),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<slug:slug>/", views.cart_add, name="cart_add"),
    path("cart/remove/<slug:slug>/", views.cart_remove, name="cart_remove"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:pk>/", views.order_success, name="order_success"),
    path("failed/<int:pk>/", views.order_failed, name="order_failed"),
    path("payments/yookassa/return/<int:pk>/", views.yookassa_return, name="yookassa_return"),
    path("my-orders/", views.my_orders, name="my_orders"),
]
