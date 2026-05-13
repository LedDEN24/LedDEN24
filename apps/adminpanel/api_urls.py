from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminLogViewSet, AdminStatsAPIView

router = DefaultRouter()
router.register("admin-logs", AdminLogViewSet, basename="api-admin-logs")

urlpatterns = [
    path("admin/stats/", AdminStatsAPIView.as_view(), name="api-admin-stats"),
] + router.urls
