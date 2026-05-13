from django.urls import include, path
from rest_framework.routers import DefaultRouter

from checks.api.views import CheckViewSet


router = DefaultRouter()
router.register("checks", CheckViewSet, basename="api-checks")

urlpatterns = [
    path("", include(router.urls)),
]
