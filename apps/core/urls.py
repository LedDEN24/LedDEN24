from django.urls import path
from apps.core.views_auth import register as signup

urlpatterns = [
    path("accounts/signup/", signup, name="signup"),
]
