from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsFinanceManager

from .models import CashMeeting
from .serializers import CashMeetingSerializer
from .services import assign_cash_manager


class CashMeetingViewSet(viewsets.ModelViewSet):
    queryset = CashMeeting.objects.select_related("donation", "manager")
    serializer_class = CashMeetingSerializer
    filterset_fields = ["city", "status", "manager"]
    search_fields = ["city", "donor_contact", "donation__public_id"]

    def get_permissions(self):
        if self.action in {"assign", "update", "partial_update", "destroy", "list"}:
            return [permissions.IsAuthenticated(), IsFinanceManager()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        meeting = assign_cash_manager(self.get_object(), request.user)
        return Response(self.get_serializer(meeting).data)
