from __future__ import annotations

from django.db import transaction
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from checks.api.serializers import CheckCreateSerializer, CheckSerializer, ParserResultSerializer, RiskSerializer
from checks.models import Check, ParserResult, Risk
from checks.tasks import process_check


class OwnObjectsMixin:
    permission_classes = (permissions.IsAuthenticated,)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(verification__created_by=self.request.user)
        return super().filter_queryset(queryset)


class CheckViewSet(viewsets.ModelViewSet):
    serializer_class = CheckSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("status", "risk_score", "cadastral_number", "inn")
    search_fields = ("address", "cadastral_number", "full_name", "phone", "email", "inn")
    ordering_fields = ("created_at", "risk_score", "status")
    ordering = ("-created_at",)

    def get_queryset(self):
        return (
            Check.objects.filter(created_by=self.request.user)
            .prefetch_related("parser_results", "risks", "properties", "owners", "court_cases", "debts")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CheckCreateSerializer
        return CheckSerializer

    def perform_create(self, serializer):
        check = serializer.save(created_by=self.request.user)
        transaction.on_commit(lambda: process_check.delay(check.pk))

    @action(detail=True, methods=["post"])
    def restart(self, request, pk=None):
        check = self.get_object()
        process_check.delay(check.pk)
        return Response({"status": "queued", "check_id": check.pk})

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        check = self.get_object()
        return Response(CheckSerializer(check, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="report.pdf")
    def report_pdf(self, request, pk=None):
        check = self.get_object()
        if not check.report_pdf:
            return HttpResponse("PDF еще не сформирован", status=404)
        return HttpResponse(check.report_pdf.open("rb").read(), content_type="application/pdf")


class ParserResultViewSet(OwnObjectsMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ParserResultSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("source", "status", "verification")
    search_fields = ("source", "error")
    ordering_fields = ("fetched_at", "duration_ms", "source")
    ordering = ("-fetched_at",)

    def get_queryset(self):
        return ParserResult.objects.select_related("verification").filter(verification__created_by=self.request.user)


class RiskViewSet(OwnObjectsMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RiskSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("severity", "code", "verification")
    search_fields = ("title", "description", "code")
    ordering_fields = ("weight", "created_at")
    ordering = ("-weight",)

    def get_queryset(self):
        return Risk.objects.select_related("verification", "parser_result").filter(verification__created_by=self.request.user)
