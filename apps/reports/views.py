from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsFinanceManager

from .models import Report
from .serializers import ReportSerializer
from .services import generate_donations_csv


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related("generated_by")
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]
    filterset_fields = ["report_type", "generated_by"]

    @action(detail=False, methods=["post"], url_path="donations-export")
    def donations_export(self, request):
        report = generate_donations_csv(user=request.user, filters=request.data.get("filters", {}))
        return Response(self.get_serializer(report).data)
