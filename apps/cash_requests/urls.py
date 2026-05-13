from rest_framework.routers import DefaultRouter

from .views import CashMeetingViewSet

router = DefaultRouter()
router.register("cash-meetings", CashMeetingViewSet, basename="cash-meetings")

urlpatterns = router.urls
