from rest_framework import viewsets

from apps.adminpanel.permissions import IsFinancialManager
from .models import ReportExport
from .serializers import ReportExportSerializer
from .tasks import build_report_export


class ReportExportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportExportSerializer
    permission_classes = [IsFinancialManager]

    def get_queryset(self):
        return ReportExport.objects.filter(requested_by=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save()
        build_report_export.delay(report.pk)
