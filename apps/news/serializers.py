from rest_framework import serializers

from .models import NewsArticle


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ["id", "title", "slug", "excerpt", "body", "image", "status", "published_at", "created_at"]
        read_only_fields = ["slug", "created_at"]
