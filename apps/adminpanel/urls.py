from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminDashboardView, AdminLogViewSet, AdminStatsAPIView

router = DefaultRouter()
router.register("admin-logs", AdminLogViewSet, basename="admin-logs")

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("api/admin/stats/", AdminStatsAPIView.as_view(), name="api-admin-stats"),
] + router.urls
