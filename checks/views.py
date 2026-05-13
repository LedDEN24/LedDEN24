from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from checks.forms import CheckForm
from checks.models import Check
from checks.reports import ReportGenerator
from checks.tasks import run_check_parsing


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "checks/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checks = Check.objects.filter(user=self.request.user)
        context.update(
            {
                "total_checks": checks.count(),
                "high_risk_checks": checks.filter(risk_level__in=["high", "critical"]).count(),
                "running_checks": checks.filter(status__in=["pending", "running"]).count(),
                "latest_checks": checks[:5],
            }
        )
        return context


class CheckCreateView(LoginRequiredMixin, CreateView):
    form_class = CheckForm
    template_name = "checks/check_form.html"
    success_url = reverse_lazy("checks:history")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        run_check_parsing.delay(self.object.id)
        return response


class CheckHistoryView(LoginRequiredMixin, ListView):
    model = Check
    template_name = "checks/history.html"
    context_object_name = "checks"
    paginate_by = 20

    def get_queryset(self):
        return Check.objects.filter(user=self.request.user).order_by("-created_at")


class CheckReportView(LoginRequiredMixin, DetailView):
    model = Check
    template_name = "checks/report.html"
    context_object_name = "check"

    def get_queryset(self):
        return Check.objects.filter(user=self.request.user).prefetch_related(
            "parser_results", "risks", "properties", "owners", "court_cases", "debts"
        )


def report_pdf_view(request, pk: int):
    if not request.user.is_authenticated:
        return redirect("checks:login")
    check = Check.objects.get(pk=pk, user=request.user)
    pdf = ReportGenerator().render_pdf(check)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="check-{check.pk}.pdf"'
    return response
