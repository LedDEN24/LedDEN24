from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets

from .models import NewsArticle
from .serializers import NewsArticleSerializer


class NewsArticleViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        qs = NewsArticle.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(status=NewsArticle.Status.PUBLISHED)
        return qs

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, status=NewsArticle.Status.PUBLISHED)
    return render(request, "pages/news_detail.html", {"article": article})
