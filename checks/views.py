from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from checks.forms import CheckForm
from checks.models import Check
from checks.tasks import process_check


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "checks/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checks = Check.objects.filter(created_by=self.request.user)
        context["total_checks"] = checks.count()
        context["completed_checks"] = checks.filter(status="completed").count()
        context["high_risk_checks"] = checks.filter(risk_score__gte=60).count()
        context["recent_checks"] = checks[:5]
        return context


class CheckCreateView(LoginRequiredMixin, CreateView):
    model = Check
    form_class = CheckForm
    template_name = "checks/check_form.html"
    success_url = reverse_lazy("history")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        transaction.on_commit(lambda: process_check.delay(self.object.pk))
        return response


class CheckHistoryView(LoginRequiredMixin, ListView):
    model = Check
    template_name = "checks/history.html"
    context_object_name = "checks"
    paginate_by = 20

    def get_queryset(self):
        queryset = Check.objects.filter(created_by=self.request.user).order_by("-created_at")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        if q:
            queryset = queryset.filter(address__icontains=q)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Check
    template_name = "checks/report_detail.html"
    context_object_name = "check"

    def get_queryset(self):
        return (
            Check.objects.filter(created_by=self.request.user)
            .prefetch_related("parser_results", "risks", "properties", "owners", "court_cases", "debts")
            .order_by("-created_at")
        )
