from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import CheckViewSet

router = DefaultRouter()
router.register("", CheckViewSet, basename="checks")

urlpatterns = router.urls
