from rest_framework.routers import DefaultRouter

from .views import AdminLogViewSet


router = DefaultRouter()
router.register("logs", AdminLogViewSet, basename="admin-logs")

urlpatterns = router.urls
