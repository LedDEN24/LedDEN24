from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import decorators, permissions, response, status, viewsets

from checks.api.serializers import CheckCreateSerializer, CheckSerializer
from checks.models import Check
from checks.reports import ReportGenerator
from checks.tasks import run_check_parsing


class CheckViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ("status", "risk_level", "inn", "cadastral_number")
    search_fields = ("address", "full_name", "phone", "email", "inn", "cadastral_number")
    ordering_fields = ("created_at", "risk_score", "completed_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return (
            Check.objects.filter(user=self.request.user)
            .prefetch_related("parser_results", "risks", "properties", "owners", "court_cases", "debts")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CheckCreateSerializer
        return CheckSerializer

    def perform_create(self, serializer):
        check = serializer.save(user=self.request.user)
        run_check_parsing.delay(check.id)

    @decorators.action(detail=True, methods=["post"])
    def rerun(self, request, pk=None):
        check = self.get_object()
        run_check_parsing.delay(check.id)
        return response.Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)

    @decorators.action(detail=True, methods=["get"], url_path="report/html")
    def report_html(self, request, pk=None):
        check = self.get_object()
        return HttpResponse(ReportGenerator().render_html(check))

    @decorators.action(detail=True, methods=["get"], url_path="report/pdf")
    def report_pdf(self, request, pk=None):
        check = get_object_or_404(self.get_queryset(), pk=pk)
        pdf = ReportGenerator().render_pdf(check)
        response_obj = HttpResponse(pdf, content_type="application/pdf")
        response_obj["Content-Disposition"] = f'attachment; filename="check-{check.pk}.pdf"'
        return response_obj
