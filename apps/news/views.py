from django.views.generic import DetailView
from rest_framework import viewsets

from apps.users.permissions import IsModeratorOrReadOnly

from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsModeratorOrReadOnly]
    filterset_fields = ["status"]
    search_fields = ["title", "excerpt", "body"]
    ordering_fields = ["published_at", "created_at"]


class ArticleDetailView(DetailView):
    model = Article
    template_name = "news/detail.html"
    context_object_name = "article"
    slug_field = "slug"
