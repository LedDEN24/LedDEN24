from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search_page, name="search_page"),
    path("api/search/", views.search_api, name="search_api"),
    path("contact/", views.contact, name="contact"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("lead/", views.lead_create, name="lead_create"),
]
