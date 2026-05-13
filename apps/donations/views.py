from django.http import FileResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsFinanceManager

from .models import Donation
from .serializers import DonationCreateSerializer, DonationSerializer
from .services import approve_donation, generate_receipt_pdf, reject_donation


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.select_related("donor", "project", "approved_by").prefetch_related("transactions")
    serializer_class = DonationSerializer
    filterset_fields = ["status", "method", "currency", "project"]
    search_fields = ["public_id", "donor_email", "donor_name", "payment_reference"]
    ordering_fields = ["created_at", "amount", "risk_score"]

    def get_permissions(self):
        if self.action in {"approve", "reject", "partial_update", "update", "destroy"}:
            return [permissions.IsAuthenticated(), IsFinanceManager()]
        if self.action in {"list", "retrieve", "receipt"}:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return DonationCreateSerializer
        return DonationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_finance_staff:
            return queryset
        if user.is_authenticated:
            return queryset.filter(donor=user)
        return queryset.none()

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()
        return Response(DonationSerializer(donation, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        donation = self.get_object()
        approve_donation(donation, request.user)
        return Response(self.get_serializer(donation).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        donation = self.get_object()
        reject_donation(donation, request.user, request.data.get("reason", ""))
        return Response(self.get_serializer(donation).data)

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        donation = self.get_object()
        if donation.status != Donation.Status.APPROVED:
            return Response({"detail": "Receipt is available after approval."}, status=400)
        if not donation.receipt_pdf:
            generate_receipt_pdf(donation)
        return FileResponse(donation.receipt_pdf.open("rb"), as_attachment=True, filename=f"{donation.public_id}.pdf")
