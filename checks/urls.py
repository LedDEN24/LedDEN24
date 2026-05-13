from django.urls import path

from checks.views import CheckCreateView, CheckHistoryView, DashboardView, ReportDetailView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("checks/new/", CheckCreateView.as_view(), name="check-create"),
    path("checks/history/", CheckHistoryView.as_view(), name="history"),
    path("checks/<int:pk>/report/", ReportDetailView.as_view(), name="report-detail"),
]
