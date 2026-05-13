from django.http import FileResponse
from rest_framework import decorators, permissions, response, status, viewsets

from apps.adminpanel.permissions import IsFinancialManager
from .models import Donation
from .serializers import CashDonationSerializer, CryptoDonationSerializer, DonationReviewSerializer, DonationSerializer
from .services import approve_donation, reject_donation
from .tasks import generate_receipt_pdf


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    throttle_scope = "donation"

    def get_queryset(self):
        qs = Donation.objects.select_related("project", "donor").prefetch_related("allocations")
        if self.request.user.is_authenticated and getattr(self.request.user, "is_finance_staff", False):
            return qs
        if self.request.user.is_authenticated:
            return qs.filter(donor=self.request.user)
        return qs.none()

    def get_permissions(self):
        if self.action in {"create", "crypto", "cash"}:
            return [permissions.AllowAny()]
        if self.action in {"review", "allocate"}:
            return [IsFinancialManager()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["post"], serializer_class=CryptoDonationSerializer)
    def crypto(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()
        return response.Response(DonationSerializer(donation, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=["post"], serializer_class=CashDonationSerializer)
    def cash(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()
        return response.Response(DonationSerializer(donation, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"], serializer_class=DonationReviewSerializer)
    def review(self, request, pk=None):
        donation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["status"] == Donation.Status.APPROVED:
            donation = approve_donation(donation, request.user)
            generate_receipt_pdf.delay(donation.pk)
        else:
            donation = reject_donation(donation, request.user, serializer.validated_data.get("reason", "Rejected by financial manager"))
        return response.Response(DonationSerializer(donation, context={"request": request}).data)

    @decorators.action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        donation = self.get_object()
        transaction = getattr(donation, "transaction", None)
        if not transaction or not transaction.receipt:
            generate_receipt_pdf.delay(donation.pk)
            return response.Response({"detail": "Receipt is being generated."}, status=status.HTTP_202_ACCEPTED)
        return FileResponse(transaction.receipt.open("rb"), as_attachment=True, filename=f"{donation.reference}.pdf")
