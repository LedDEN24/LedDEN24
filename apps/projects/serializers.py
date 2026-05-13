from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "title", "slug", "short_description", "description", "goal_amount", "raised_amount", "currency", "progress_percent", "status", "cover_image", "location", "beneficiaries_count", "is_featured", "starts_at", "ends_at", "seo_title", "seo_description", "created_at"]
        read_only_fields = ["id", "slug", "raised_amount", "progress_percent", "created_at"]
