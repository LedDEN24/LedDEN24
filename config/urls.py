from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.projects.sitemaps import ProjectSitemap
from apps.news.sitemaps import NewsSitemap


sitemaps = {
    "projects": ProjectSitemap,
    "news": NewsSitemap,
}

api_patterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", include("apps.users.urls")),
    path("projects/", include("apps.projects.urls")),
    path("news/", include("apps.news.urls")),
    path("donations/", include("apps.donations.urls")),
    path("crypto/", include("apps.crypto_payments.urls")),
    path("cash/", include("apps.cash_requests.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("reports/", include("apps.reports.urls")),
    path("adminpanel/", include("apps.adminpanel.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_patterns)),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
] + i18n_patterns(
    path("", include("apps.projects.web_urls")),
    path("account/", include("apps.users.web_urls")),
    path("dashboard/", include("apps.adminpanel.web_urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
