from django.urls import path

from .views import account_dashboard


urlpatterns = [
    path("", account_dashboard, name="account_dashboard"),
]
