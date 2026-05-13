from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CashCollectionPointViewSet, CashMeetingViewSet


router = DefaultRouter()
router.register("meetings", CashMeetingViewSet, basename="cash-meetings")
router.register("points", CashCollectionPointViewSet, basename="cash-points")

urlpatterns = [path("", include(router.urls))]
