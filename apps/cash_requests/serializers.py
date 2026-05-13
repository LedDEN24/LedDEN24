from rest_framework import serializers

from .models import CashMeeting


class CashMeetingSerializer(serializers.ModelSerializer):
    donation_public_id = serializers.CharField(source="donation.public_id", read_only=True)

    class Meta:
        model = CashMeeting
        fields = ["id", "donation", "donation_public_id", "city", "preferred_datetime", "meeting_address", "manager", "status", "manager_notes", "donor_contact", "created_at", "updated_at"]
        read_only_fields = ["id", "donation_public_id", "created_at", "updated_at"]
