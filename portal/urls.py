from django.urls import path

from . import views


app_name = "portal"


urlpatterns = [
    path("", views.home, name="home"),
    path("demo/", views.demo_request, name="demo-request"),
    path("tariffs/", views.tariffs, name="tariffs"),
    path("privacy/", views.privacy_policy, name="privacy-policy"),
    path("agreement-personal-data/", views.personal_data_consent, name="personal-data-consent"),
    path("contacts/", views.contacts, name="contacts"),
    path("sources/", views.sources, name="sources"),
    path("api/sources/", views.sources_api, name="sources-api"),
    path("documents/<slug:slug>/", views.document_detail, name="document-detail"),
]
