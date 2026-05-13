from __future__ import annotations

from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAnalystOrManager
from apps.audit.models import AuditLog
from apps.reports.services import ReportFormat, ReportService

from .models import Check
from .serializers import CheckCreateSerializer, CheckDetailSerializer
from .tasks import run_property_check


class CheckViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Check.objects.select_related("property", "owner")
        .prefetch_related("parser_results", "risks", "court_cases", "debts", "bankruptcy_records", "scraped_ads")
        .all()
    )
    permission_classes = [IsAnalystOrManager]
    throttle_scope = "checks"

    def get_serializer_class(self):
        if self.action == "create":
            return CheckCreateSerializer
        return CheckDetailSerializer

    def perform_create(self, serializer: CheckCreateSerializer) -> None:
        check = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditLog.Action.CHECK_CREATED,
            object_type="Check",
            object_id=str(check.id),
            metadata={"cadastral_number": check.property.cadastral_number},
        )
        run_property_check.delay(str(check.id))

    def create(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response

    @action(detail=True, methods=["post"])
    def restart(self, request, pk=None):  # type: ignore[no-untyped-def]
        check = self.get_object()
        check.status = Check.Status.QUEUED
        check.error_message = ""
        check.save(update_fields=["status", "error_message", "updated_at"])
        run_property_check.delay(str(check.id))
        return Response(CheckDetailSerializer(check, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["get"], throttle_scope="reports")
    def report(self, request, pk=None):  # type: ignore[no-untyped-def]
        check = self.get_object()
        fmt = request.query_params.get("format", ReportFormat.JSON)
        payload, content_type, filename = ReportService().render(check, fmt)
        AuditLog.objects.create(
            actor=request.user,
            action=AuditLog.Action.REPORT_GENERATED,
            object_type="Check",
            object_id=str(check.id),
            metadata={"format": fmt},
        )
        if isinstance(payload, (dict, list)):
            return Response(payload)
        response = HttpResponse(payload, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
