from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DonationHistoryView, EmailVerificationView, ProfileView, RegisterView, SavedPaymentMethodViewSet


router = DefaultRouter()
router.register("payment-methods", SavedPaymentMethodViewSet, basename="payment-methods")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("profile/", ProfileView.as_view(), name="api-profile"),
    path("verify-email/", EmailVerificationView.as_view(), name="api-verify-email"),
    path("donations/", DonationHistoryView.as_view(), name="api-donation-history"),
    path("", include(router.urls)),
]
