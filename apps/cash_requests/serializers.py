from rest_framework import serializers

from .models import CashCollectionPoint, CashMeeting


class CashMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashMeeting
        fields = [
            "id",
            "donation",
            "city",
            "preferred_place",
            "preferred_time",
            "manager",
            "scheduled_time",
            "status",
            "manager_comment",
            "created_at",
        ]
        read_only_fields = ["manager", "created_at"]


class CashCollectionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashCollectionPoint
        fields = ["id", "city", "address", "latitude", "longitude", "minimum_amount", "is_active"]
