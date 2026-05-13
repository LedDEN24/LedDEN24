from rest_framework import serializers

from .models import AdminLog


class AdminLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AdminLog
        fields = ["id", "actor", "actor_email", "action", "object_type", "object_id", "ip_address", "user_agent", "metadata", "created_at"]
        read_only_fields = fields
