from django.utils import timezone
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "channel", "level", "link", "read_at", "created_at"]
        read_only_fields = ["created_at"]

    def update(self, instance, validated_data):
        if validated_data.pop("read_at", None) is None:
            instance.read_at = timezone.now()
        return super().update(instance, validated_data)
