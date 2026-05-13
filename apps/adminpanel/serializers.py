from rest_framework import serializers

from .models import AdminLog


class AdminLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AdminLog
        fields = ["id", "actor", "actor_email", "action", "content_type", "object_id", "message", "metadata", "ip_address", "created_at"]
        read_only_fields = fields
