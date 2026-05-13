from rest_framework import serializers

from .models import Donation, Transaction
from .services import register_donation


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "gateway", "external_id", "status", "amount", "currency", "raw_payload", "checked_by", "checked_at", "created_at"]
        read_only_fields = ["id", "checked_by", "checked_at", "created_at"]


class DonationSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = Donation
        fields = ["id", "public_id", "donor", "donor_name", "donor_email", "project", "project_title", "amount", "currency", "method", "status", "purpose", "comment", "is_anonymous", "receipt_upload", "receipt_pdf", "payment_reference", "risk_score", "suspicious_reason", "approved_by", "approved_at", "rejected_reason", "transactions", "created_at", "updated_at"]
        read_only_fields = ["id", "public_id", "donor", "status", "payment_reference", "risk_score", "suspicious_reason", "approved_by", "approved_at", "rejected_reason", "receipt_pdf", "created_at", "updated_at"]


class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["donor_name", "donor_email", "project", "amount", "currency", "method", "purpose", "comment", "is_anonymous", "receipt_upload"]

    def create(self, validated_data):
        request = self.context.get("request")
        donor = request.user if request and request.user.is_authenticated else None
        return register_donation(
            donor=donor,
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
            **validated_data,
        )
