from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet

router = DefaultRouter()
router.register("news", ArticleViewSet, basename="news")

urlpatterns = router.urls
