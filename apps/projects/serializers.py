from rest_framework import serializers

from .models import Project, ProjectUpdate


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectUpdate
        fields = ["id", "title", "body", "image", "published_at"]


class ProjectSerializer(serializers.ModelSerializer):
    progress_percent = serializers.IntegerField(read_only=True)
    updates = ProjectUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "description",
            "country",
            "city",
            "cover_image",
            "goal_amount",
            "collected_amount",
            "currency",
            "beneficiaries_count",
            "status",
            "featured",
            "progress_percent",
            "starts_at",
            "ends_at",
            "updates",
            "created_at",
        ]
        read_only_fields = ["slug", "collected_amount", "created_at"]
