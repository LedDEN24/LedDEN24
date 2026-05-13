from django.urls import path

from apps.news.views import news_detail
from .views import home, project_detail


urlpatterns = [
    path("", home, name="home"),
    path("projects/<slug:slug>/", project_detail, name="project_detail"),
    path("news/<slug:slug>/", news_detail, name="news_detail"),
]
