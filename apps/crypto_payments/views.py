from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsFinanceManager

from .models import CryptoPayment, CryptoWallet
from .serializers import CryptoPaymentSerializer, CryptoWalletSerializer
from .services import mark_crypto_confirmed


class CryptoWalletViewSet(viewsets.ModelViewSet):
    queryset = CryptoWallet.objects.all()
    serializer_class = CryptoWalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]
    filterset_fields = ["currency", "network", "is_active"]


class CryptoPaymentViewSet(viewsets.ModelViewSet):
    queryset = CryptoPayment.objects.select_related("donation", "wallet")
    serializer_class = CryptoPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]
    filterset_fields = ["status", "network", "wallet"]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        payment = mark_crypto_confirmed(self.get_object(), request.user)
        return Response(self.get_serializer(payment).data)
