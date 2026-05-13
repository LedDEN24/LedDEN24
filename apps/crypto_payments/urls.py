from rest_framework.routers import DefaultRouter

from .views import CryptoPaymentViewSet, CryptoWalletViewSet

router = DefaultRouter()
router.register("crypto-wallets", CryptoWalletViewSet, basename="crypto-wallets")
router.register("crypto-payments", CryptoPaymentViewSet, basename="crypto-payments")

urlpatterns = router.urls
