from __future__ import annotations

import hashlib
from typing import Any

from django.db import transaction
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.checks.audit import write_audit_log
from apps.checks.models import AuditLog, Check, Owner, Property
from apps.checks.permissions import IsAnalystOrOwner
from apps.checks.serializers import CheckSerializer, PropertyCheckCreateSerializer, RiskSerializer
from apps.checks.tasks import run_property_check
from reports.services import ReportFormat, ReportService


class CheckViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CheckSerializer
    permission_classes = [IsAnalystOrOwner]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "checks"

    def get_queryset(self):
        queryset = (
            Check.objects.select_related("property", "requested_by")
            .prefetch_related("risks", "parser_results")
            .order_by("-created_at")
        )
        if self.request.user.is_staff or self.request.user.groups.filter(name="analyst").exists():
            return queryset
        return queryset.filter(requested_by=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return PropertyCheckCreateSerializer
        return CheckSerializer

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        seller = data["seller"]
        property_obj = Property.objects.create(
            address=data["address"],
            cadastral_number=data["cadastral_number"],
            region=data.get("region", ""),
        )
        Owner.objects.create(
            property=property_obj,
            full_name=seller["full_name"],
            phone=seller.get("phone", ""),
            email=seller.get("email", ""),
            inn=seller.get("inn", ""),
            normalized_name_hash=_stable_hash(seller["full_name"]),
        )
        check = Check.objects.create(property=property_obj, requested_by=request.user)
        write_audit_log(
            request=request,
            action=AuditLog.Action.CHECK_CREATED,
            object_id=str(check.id),
            metadata={"cadastral_number": property_obj.cadastral_number},
        )
        return Response(CheckSerializer(check, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def run(self, request: Request, pk: str | None = None) -> Response:
        check = self.get_object()
        check.status = Check.Status.QUEUED
        check.save(update_fields=["status", "updated_at"])
        run_property_check.delay(str(check.id))
        write_audit_log(request=request, action=AuditLog.Action.CHECK_QUEUED, object_id=str(check.id))
        return Response({"id": str(check.id), "status": check.status})

    @action(detail=True, methods=["get"])
    def risks(self, request: Request, pk: str | None = None) -> Response:
        check = self.get_object()
        return Response(RiskSerializer(check.risks.order_by("-score_impact"), many=True).data)

    @action(detail=True, methods=["get"])
    def report(self, request: Request, pk: str | None = None) -> HttpResponse:
        check = self.get_object()
        report_format = ReportFormat(request.query_params.get("format", ReportFormat.JSON))
        content, content_type, filename = ReportService().render(check, report_format)
        write_audit_log(
            request=request,
            action=AuditLog.Action.REPORT_DOWNLOADED,
            object_id=str(check.id),
            metadata={"format": report_format},
        )
        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.casefold().strip().encode("utf-8")).hexdigest()
