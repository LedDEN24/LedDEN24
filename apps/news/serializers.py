from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "slug", "excerpt", "body", "status", "author", "author_name", "cover_image", "published_at", "seo_title", "seo_description", "created_at"]
        read_only_fields = ["id", "slug", "author", "author_name", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)
