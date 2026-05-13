from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CryptoPaymentViewSet, CryptoWalletViewSet


router = DefaultRouter()
router.register("wallets", CryptoWalletViewSet, basename="crypto-wallets")
router.register("payments", CryptoPaymentViewSet, basename="crypto-payments")

urlpatterns = [path("", include(router.urls))]
