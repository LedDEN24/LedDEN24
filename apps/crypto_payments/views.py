from rest_framework import permissions, viewsets

from apps.adminpanel.permissions import IsFinancialManager
from .models import CryptoPayment, CryptoWallet
from .serializers import CryptoPaymentSerializer, CryptoWalletSerializer


class CryptoWalletViewSet(viewsets.ModelViewSet):
    serializer_class = CryptoWalletSerializer

    def get_queryset(self):
        qs = CryptoWallet.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [IsFinancialManager()]


class CryptoPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CryptoPaymentSerializer
    permission_classes = [IsFinancialManager]
    queryset = CryptoPayment.objects.select_related("donation", "wallet")
