from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.news.views import ArticleDetailView
from apps.projects.views import ProjectDetailView
from config.sitemaps import ArticleSitemap, ProjectSitemap, StaticViewSitemap
from config.views import DashboardView, DonationPageView, HomeView, robots_txt

sitemaps = {"static": StaticViewSitemap, "projects": ProjectSitemap, "news": ArticleSitemap}

api_patterns = [
    path("", include("apps.users.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.news.urls")),
    path("", include("apps.donations.urls")),
    path("", include("apps.crypto_payments.urls")),
    path("", include("apps.cash_requests.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.reports.urls")),
    path("", include("apps.adminpanel.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("donate/", DonationPageView.as_view(), name="donate"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project-detail"),
    path("news/<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("platform/", include("apps.adminpanel.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/", include(api_patterns)),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots-txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
