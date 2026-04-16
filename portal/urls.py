from django.urls import path

from . import views


app_name = "portal"


urlpatterns = [
    path("", views.home, name="home"),
    path("sources/", views.sources, name="sources"),
    path("api/sources/", views.sources_api, name="sources-api"),
    path("documents/<slug:slug>/", views.document_detail, name="document-detail"),
]
