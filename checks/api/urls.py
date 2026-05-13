from django.urls import include, path
from rest_framework.routers import DefaultRouter

from checks.api.views import CheckViewSet, ParserResultViewSet, RiskViewSet

router = DefaultRouter()
router.register("checks", CheckViewSet, basename="checks")
router.register("parser-results", ParserResultViewSet, basename="parser-results")
router.register("risks", RiskViewSet, basename="risks")

urlpatterns = [
    path("", include(router.urls)),
]
