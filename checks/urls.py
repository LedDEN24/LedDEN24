from django.contrib.auth import views as auth_views
from django.urls import path

from checks.views import (
    CheckCreateView,
    CheckHistoryView,
    CheckReportView,
    DashboardView,
    report_pdf_view,
)


app_name = "checks"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("checks/new/", CheckCreateView.as_view(), name="check-create"),
    path("checks/history/", CheckHistoryView.as_view(), name="history"),
    path("checks/<int:pk>/", CheckReportView.as_view(), name="report"),
    path("checks/<int:pk>/pdf/", report_pdf_view, name="report-pdf"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="checks/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
