from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.checks.views import CheckViewSet

router = DefaultRouter()
router.register("checks", CheckViewSet, basename="checks")

urlpatterns = router.urls
