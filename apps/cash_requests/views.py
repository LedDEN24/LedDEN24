from rest_framework import permissions, viewsets

from apps.adminpanel.permissions import IsFinancialManager
from .models import CashCollectionPoint, CashMeeting
from .serializers import CashCollectionPointSerializer, CashMeetingSerializer


class CashMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = CashMeetingSerializer

    def get_queryset(self):
        qs = CashMeeting.objects.select_related("donation", "manager")
        if self.request.user.is_authenticated and getattr(self.request.user, "is_finance_staff", False):
            return qs
        return qs.filter(donation__donor=self.request.user)

    def perform_update(self, serializer):
        serializer.save(manager=self.request.user)


class CashCollectionPointViewSet(viewsets.ModelViewSet):
    serializer_class = CashCollectionPointSerializer
    queryset = CashCollectionPoint.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [IsFinancialManager()]
